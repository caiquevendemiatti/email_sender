from celery import shared_task
from emails_controller.send_email.SendEmail import send_email as _send_email


@shared_task
def executar_envio_emails():
    _send_email()
