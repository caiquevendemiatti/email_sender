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
        self.email_block_len = 10
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SEND E-MAIL CLASS")

    def create_email_task(self, task_name, subject):
        contact_list = Contato.objects.filter(ativo=True, excluido=False)

        for contact in contact_list:
            task_envio = Task_Envio(
                tarefa=task_name,
                assunto=subject,
                contato=contact,
                enviado=False
            )
            task_envio.save()

    def send_email_by_vendor(self):
        self.logger.debug(f"List vendors for sending e-mails")
        vendors = Colaborador.objects.filter(habilitado=True)

        for vendor in vendors:
            self.run_email_tasks(vendor)

    def run_email_tasks(self, vendor):
        self.logger.debug(f"Run e-mail tasks {vendor.nome}")
        subject = 'Hidrotube em Novo Endereço'
        from_email = settings.EMAIL_HOST_USER
        vendor_name = vendor.nome
        vendor_email = vendor.e_mail
        max_tasks = self.email_block_len
        whatsapp = vendor.whatsapp
        ddd = vendor.ddd

        self.logger.debug("Lista tarefas de envio pendentes")
        #TODO: Inserir limite no final da seleção de tarefas para evitar tempos de execução muito longos
        tasks = Task_Envio.objects.filter(enviado=False, contato__colaborador_responsavel=vendor)
        to = []
        pk = []
        to_counter = 0
        sent = 0
        tasks_len = len(tasks)

        if tasks_len < max_tasks:
            max_tasks = tasks_len

        for task in tasks:
            to_counter = to_counter + 1  # Counters for triggering e-mail sending
            sent = sent + 1

            to.append(task.contato.e_mail)  # Gets the e-mail address for sending, and pk for updating DB
            pk.append(task.pk)

            # When reached the number of contacts for a single e-mail proceed email send task
            if to_counter == max_tasks:
                self.logger.debug(f"Enviando para:  {to} - Whatsapp: {whatsapp}")
                success = self.send_new_address(to, 'Tarefa Teste', ddd, whatsapp, vendor_name, vendor_email)

                if success:
                    self.mark_task_complete(pk)
                else:
                    self.mark_task_error(pk)

                # If the number of pending contacts is less then email block, reduce e-mail block
                if (tasks_len - sent) < max_tasks:
                    max_tasks = (tasks_len - sent)

                to_counter = 0
                pk = []
                to = []

    def send_new_address(self, to, subject, ddd, whatsapp, vendor_name, vendor_email):
        self.logger.debug("Send_new_address")
        from_email = settings.EMAIL_HOST_USER
        link_wa = f'https://wa.me/55{ddd}{whatsapp}'
        format_phone = f'({ddd}) {whatsapp[0:5]}-{whatsapp[5:]}'
        add_content = {'vendor_name': vendor_name,
                       'vendor_email': vendor_email,
                        'link_wa': link_wa,
                       'phone_number': format_phone,
                       'link_cancel_inscr': 'http://marketing.hidrotube.com.br/cancelar_inscricao'}
        html_content = render_to_string('novo_endereco.html', add_content)
        text_content = strip_tags(html_content)

        message = EmailMultiAlternatives(subject, text_content, f"Hidrotube - Marketing <{from_email}>", bcc=to)
        message.attach_alternative(html_content, "text/html")

        message.attach(self.img_data(
            'email_sender/templates/images/logo_ht_grande.png',
            '<image1>'))
        message.attach(self.img_data(
            'email_sender/templates/images/gopr3487r.jpg',
            '<image2>'))
        message.attach(self.img_data(
            'email_sender/templates/images/facebook-circle-colored.png',
            '<image3>'))
        message.attach(self.img_data(
            'email_sender/templates/images/instagram-circle-colored.png',
            '<image4>'))
        message.attach(self.img_data(
            'email_sender/templates/images/logo_ht.png',
            '<image5>'))
        try:
            message.send()
            return True
        except SMTPException as e:
            self.logger.debug('There was an error sending an email: ', e)
            return False
        except:
            self.logger.debug("Unknown error sending email")
            return False


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