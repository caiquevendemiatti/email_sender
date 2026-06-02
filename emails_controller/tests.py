from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import MagicMock, patch, PropertyMock
from django.db.models.fields.files import ImageFieldFile

from emails_controller.models import ConteudoEmail, Colaborador, Contato
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
