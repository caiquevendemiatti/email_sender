from django.core.management.base import BaseCommand
from emails_controller.aux_files.contact_import import processar_importacao, formatar_resultado


class Command(BaseCommand):
    help = "Importa planilha Excel para atualizar a base de contatos"

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho do arquivo Excel a importar')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a importação sem salvar nenhuma alteração',
        )

    def handle(self, *args, **options):
        filepath = options['arquivo']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('--- MODO DRY-RUN: nenhuma alteração será salva ---\n'))

        try:
            with open(filepath, 'rb') as f:
                result = processar_importacao(f, dry_run=dry_run)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Arquivo não encontrado: {filepath}'))
            return

        self.stdout.write(formatar_resultado(result, dry_run=dry_run))

        if result['errors']:
            raise SystemExit(1)
