from django.core.management.base import BaseCommand
from emails_controller.aux_files.load_data import LoadData

class Command(BaseCommand):
    help = "Load EMails"

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        load_data = LoadData()
        load_data.load_email_list_by_vendor(filename='emails_controller/aux_files/Lista_Email_Vendedor.xlsx',
                                            vendor_name='Caique Vendemiatti')


