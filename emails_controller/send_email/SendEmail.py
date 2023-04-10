from django.conf import settings
from django.db.models import F
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from smtplib import SMTPException

import logging

from django.contrib.staticfiles import finders
from functools import lru_cache

from emails_controller.models import Task_Envio, Contato, Colaborador


class SendEmail:
    def __init__(self):
        self.receivers_block_limit = 50
        self.receivers_limit_hour = 900
        self.receivers_count = 0
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SEND E-MAIL CLASS")

    def send_email_by_vendor(self):
        self.logger.debug(f"List vendors for sending e-mails")
        vendors = Colaborador.objects.filter(habilitado=True)

        for vendor in vendors:
            if self.receivers_count < self.receivers_limit_hour:
                self.run_email_tasks(vendor)

    def run_email_tasks(self, vendor):
        self.logger.debug(f"Run e-mail tasks {vendor.nome}")

        vendor_name = vendor.nome
        vendor_email = vendor.e_mail
        whatsapp = vendor.whatsapp
        ddd = vendor.ddd

        max_receivers_by_message = self.receivers_block_limit
        select_task_max_len = self.receivers_limit_hour - self.receivers_count

        if select_task_max_len <= 0:
            return

        tasks = Task_Envio.objects.filter(enviado=False,
                                          contato__colaborador_responsavel=vendor,
                                          tentativas_envio__lt=2)[:select_task_max_len]
        to = []
        pk = []
        to_counter = 0
        tasks_len = len(tasks)

        if tasks_len < max_receivers_by_message:
            max_receivers_by_message = tasks_len

        for task in tasks:
            self.receivers_count = self.receivers_count + 1
            to_counter = to_counter + 1
            to.append(task.contato.e_mail)
            pk.append(task.pk)

            # When reached the number of contacts for a single e-mail proceed email send task
            if to_counter == max_receivers_by_message:
                conteudo = task.conteudo
                self.logger.debug(f"Enviando para:  {to} - Whatsapp: {whatsapp}")
                success = self.send_email(to, conteudo, ddd, whatsapp, vendor_name, vendor_email)

                if success:
                    self.mark_task_complete(pk)
                else:
                    self.mark_task_error(pk)

                # If the number of pending contacts is less than email max receivers by e-mail,
                # reduce e-mail receivers number
                if (tasks_len - to_counter) < max_receivers_by_message:
                    max_receivers_by_message = (tasks_len - to_counter)

                to_counter = 0
                pk = []
                to = []

    def send_email(self, to, conteudo_email, ddd, whatsapp, vendor_name, vendor_email):
        from_email = settings.EMAIL_HOST_USER
        link_wa = f'https://wa.me/55{ddd}{whatsapp}'
        format_phone = f'({ddd}) {whatsapp[0:5]}-{whatsapp[5:]}'
        subject = conteudo_email.assunto

        add_content = {'conteudo_titulo': conteudo_email.titulo,
                       'conteudo_texto_A': conteudo_email.conteudo_A,
                       'conteudo_texto_B': conteudo_email.conteudo_B,
                       'vendor_name': vendor_name,
                       'vendor_email': vendor_email,
                       'link_wa': link_wa,
                       'phone_number': format_phone,
                       'link_cancel_inscr': 'http://marketing.hidrotube.com.br/cancelar_inscricao'}

        html_content = render_to_string('email_hidrotube4.html', add_content)
        text_content = strip_tags(html_content)
        message = EmailMultiAlternatives(subject, text_content,
                                         from_email=f"Hidrotube - Marketing <{from_email}>",
                                         bcc=to)
        message.attach_alternative(html_content, "text/html")


        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/Campanha-NOVA-SEDE_EMKT_GABARITO_01.png',
            '/home/ubuntu/email_sender/templates/images/BannerTopo.png',
            '<image1>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/gopr3487r.jpg',
            '/home/ubuntu/email_sender/templates/images/font_Icone_WHATSAPP.png',
            '<image2>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/facebook-circle-colored.png',
            '/home/ubuntu/email_sender/templates/images/font_Icone_EMAIL.png',
            '<image3>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/instagram-circle-colored.png',
            '/home/ubuntu/email_sender/templates/images/font_Icone_TELEFONE.png',
            '<image4>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/logo_ht.png',
            '/home/ubuntu/email_sender/templates/images/Campanha-NOVA-SEDE_EMKT_GABARITO_04_S_fundo.png',
            '<image5>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/logo_ht.png',
            '/home/ubuntu/email_sender/templates/images/Icone_Localizacao_S_fundo.png',
            '<image6>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/logo_ht.png',
            '/home/ubuntu/email_sender/templates/images/Campanha-NOVA-SEDE_EMKT_GABARITO_07_S_fundo.png',
            '<image7>'))
        message.attach(self.img_data(
            # 'C:/Users/caiqu/Documents/Hidrotube/email_sender/templates/images/logo_ht.png',
            '/home/ubuntu/email_sender/templates/images/Campanha-NOVA-SEDE_EMKT_GABARITO-footer.png',
            '<image8>'))

        try:
            #result = message.send()
            self.logger.debug(f"Enviando mensagem para {len(to)} clientes")
            result = 1
            if result == 1:
                return True

            return False
        except SMTPException as e:
            self.logger.debug('There was an error sending an email: ', e)
            return False
        except Exception as error:
            self.logger.debug(f"Unknown error sending email: {error}")
        return False

    def deactivate_error_email(self):
        tasks = Task_Envio.objects.filter(enviado=False, tentativas_envio__gte=2)

        for task in tasks:
            contato = task.contato
            self.logger.debug(f"Desativando contato: {contato.razao_social}")
            contato.ativo = False
            contato.save()

    @staticmethod
    def img_data(path, cname):
        with open(path, 'rb') as f:
            logo_data = f.read()
        logo = MIMEImage(logo_data)
        logo.add_header('Content-ID', cname)
        return logo

    @staticmethod
    def mark_task_complete(ids_to_update):
        Task_Envio.objects.filter(id__in=ids_to_update).update(enviado=True)
        return

    @staticmethod
    def mark_task_error(ids_to_update):
        Task_Envio.objects.filter(id__in=ids_to_update).update(tentativas_envio=F('tentativas_envio') + 1)


def send_email():
    logger = logging.getLogger(__name__)
    logger.debug("SendEmail Func")
    send_email = SendEmail()
    send_email.send_email_by_vendor()
    send_email.deactivate_error_email()
