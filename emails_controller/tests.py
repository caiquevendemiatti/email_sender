from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from unittest.mock import MagicMock, patch, PropertyMock
from django.db.models.fields.files import ImageFieldFile
from datetime import timedelta

from emails_controller.models import ConteudoEmail, Colaborador, Contato, Task_Envio
from emails_controller.send_email.SendEmail import SendEmail


def make_fake_image():
    mock = MagicMock(spec=ImageFieldFile)
    type(mock).__bool__ = lambda self: True
    mock.open = MagicMock()
    mock.read = MagicMock(return_value=b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    mock.close = MagicMock()
    return mock


def make_conteudo(tipo, fotos=None):
    c = ConteudoEmail.__new__(ConteudoEmail)
    c.tipo_email = tipo
    c.assunto = 'Teste'
    c.titulo = 'Título'
    c.conteudo_A = 'Texto A'
    c.conteudo_B = 'Texto B'
    c.pre_imagens = 'Fotos'
    c.preheader = None
    c.foto_a = fotos[0] if fotos and len(fotos) > 0 else None
    c.foto_b = fotos[1] if fotos and len(fotos) > 1 else None
    c.foto_c = fotos[2] if fotos and len(fotos) > 2 else None
    c.foto_d = fotos[3] if fotos and len(fotos) > 3 else None
    c.foto_e = fotos[4] if fotos and len(fotos) > 4 else None
    c.foto_f = fotos[5] if fotos and len(fotos) > 5 else None
    return c


class ConteudoEmailValidationTest(TestCase):

    def test_padrao_a_4_valido(self):
        fotos = [make_fake_image() for _ in range(4)]
        c = make_conteudo('padrao_a_4', fotos)
        c.clean()  # não deve lançar exceção

    def test_padrao_a_4_sem_fotos_falha(self):
        c = make_conteudo('padrao_a_4', [])
        with self.assertRaises(ValidationError):
            c.clean()

    def test_padrao_a_4_fotos_incompletas_falha(self):
        fotos = [make_fake_image(), make_fake_image(), None, None]
        c = make_conteudo('padrao_a_4', fotos)
        with self.assertRaises(ValidationError):
            c.clean()

    def test_padrao_a_6_valido(self):
        fotos = [make_fake_image() for _ in range(6)]
        c = make_conteudo('padrao_a_6', fotos)
        c.clean()  # não deve lançar exceção

    def test_padrao_a_6_sem_fotos_falha(self):
        c = make_conteudo('padrao_a_6', [])
        with self.assertRaises(ValidationError):
            c.clean()

    def test_padrao_a_6_apenas_4_fotos_falha(self):
        fotos = [make_fake_image() for _ in range(4)] + [None, None]
        c = make_conteudo('padrao_a_6', fotos)
        with self.assertRaises(ValidationError):
            c.clean()

    def test_outros_tipos_sem_validacao_fotos(self):
        for tipo in ('6_fotos', 'sem_foto', 'apresentacao'):
            c = make_conteudo(tipo, [])
            c.clean()  # não deve lançar exceção


class SendEmailTemplateRoutingTest(TestCase):

    def _make_sender(self):
        return SendEmail()

    @patch('emails_controller.send_email.SendEmail.render_to_string', return_value='<html>')
    @patch('emails_controller.send_email.SendEmail.EmailMultiAlternatives')
    def _send(self, tipo, fotos, mock_msg_cls, mock_render):
        sender = self._make_sender()

        conteudo = make_conteudo(tipo, fotos)
        conteudo.assunto = 'Assunto'

        mock_msg = MagicMock()
        mock_msg_cls.return_value = mock_msg

        with patch.object(sender, 'img_data', return_value=MagicMock()):
            sender.send_email(
                to=['test@test.com'],
                conteudo_email=conteudo,
                ddd='19',
                whatsapp='997898757',
                vendor_name='Vendedor',
                vendor_email='v@test.com',
                vendor_id=1,
            )

        return mock_render.call_args[0][0]  # nome do template renderizado

    def test_padrao_a_4_usa_template_correto(self):
        fotos = [make_fake_image() for _ in range(4)]
        template = self._send('padrao_a_4', fotos)
        self.assertEqual(template, 'template_padrao_a_4.html')

    def test_padrao_a_6_usa_template_correto(self):
        fotos = [make_fake_image() for _ in range(6)]
        template = self._send('padrao_a_6', fotos)
        self.assertEqual(template, 'template_padrao_a_6.html')

    def test_apresentacao_usa_template_correto(self):
        fotos = [make_fake_image() for _ in range(6)]
        template = self._send('apresentacao', fotos)
        self.assertEqual(template, 'template_apresentacao.html')


class AgendamentoTaskEnvioTest(TestCase):

    def setUp(self):
        self.colaborador = Colaborador.objects.create(
            nome='Vendedor Teste',
            e_mail='vendedor@teste.com',
            ddd='19',
            whatsapp='999999999',
        )
        self.contato = Contato.objects.create(
            razao_social='Empresa Teste',
            contato='Fulano',
            e_mail='contato@teste.com',
            ativo=True,
            excluido=False,
            colaborador_responsavel=self.colaborador,
        )
        conteudo = ConteudoEmail.objects.create(
            tipo_email='sem_foto',
            assunto='Teste',
            titulo='Título',
            conteudo_A='Texto A',
        )
        self.conteudo = conteudo

    def _make_task(self, agendamento=None):
        return Task_Envio.objects.create(
            tarefa='1',
            assunto='Teste',
            contato=self.contato,
            conteudo=self.conteudo,
            enviado=False,
            data_hora_agendamento=agendamento,
        )

    def test_task_sem_agendamento_e_selecionada(self):
        self._make_task(agendamento=None)
        tasks = Task_Envio.objects.filter(
            enviado=False,
            contato__colaborador_responsavel=self.colaborador,
        ).filter(
            __import__('django.db.models', fromlist=['Q']).Q(data_hora_agendamento__isnull=True) |
            __import__('django.db.models', fromlist=['Q']).Q(data_hora_agendamento__lte=timezone.now())
        )
        self.assertEqual(tasks.count(), 1)

    def test_task_agendada_no_passado_e_selecionada(self):
        self._make_task(agendamento=timezone.now() - timedelta(hours=1))
        from django.db.models import Q
        tasks = Task_Envio.objects.filter(
            enviado=False,
            contato__colaborador_responsavel=self.colaborador,
        ).filter(
            Q(data_hora_agendamento__isnull=True) |
            Q(data_hora_agendamento__lte=timezone.now())
        )
        self.assertEqual(tasks.count(), 1)

    def test_task_agendada_no_futuro_nao_e_selecionada(self):
        self._make_task(agendamento=timezone.now() + timedelta(hours=2))
        from django.db.models import Q
        tasks = Task_Envio.objects.filter(
            enviado=False,
            contato__colaborador_responsavel=self.colaborador,
        ).filter(
            Q(data_hora_agendamento__isnull=True) |
            Q(data_hora_agendamento__lte=timezone.now())
        )
        self.assertEqual(tasks.count(), 0)
