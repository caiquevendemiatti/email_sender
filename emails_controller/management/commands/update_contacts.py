from django.core.management.base import BaseCommand
from emails_controller.aux_files.updateContacts import UpdateContacts

class Command(BaseCommand):
    help = "Send e-mail"

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        uc = UpdateContacts()


