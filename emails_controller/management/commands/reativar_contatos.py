from django.core.management.base import BaseCommand
from emails_controller.models import Contato


class Command(BaseCommand):
    help = 'Reativa todos os contatos desativados'

    def handle(self, *args, **options):
        desativados = Contato.objects.filter(ativo=False, excluido=False)
        total = desativados.count()

        if total == 0:
            self.stdout.write('Nenhum contato desativado encontrado.')
            return

        desativados.update(ativo=True)
        self.stdout.write(self.style.SUCCESS(f'{total} contato(s) reativado(s) com sucesso.'))
