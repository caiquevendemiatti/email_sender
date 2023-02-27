from django.core.management.base import BaseCommand
from emails_controller.send_email.SendEmail import send_email

class Command(BaseCommand):
    help = "Send e-mail"

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        send_email()

