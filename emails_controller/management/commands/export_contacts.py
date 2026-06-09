import io
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from emails_controller.models import Contato
from emails_controller.aux_files.contact_export import gerar_workbook_contatos


class Command(BaseCommand):
    help = "Exporta todos os contatos para uma planilha Excel"

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Caminho do arquivo de saída (padrão: contatos_<data>.xlsx na raiz do projeto)',
        )

    def handle(self, *args, **options):
        output_path = options['output']
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', '..', '..', '..',
                f'contatos_{timestamp}.xlsx'
            )
            output_path = os.path.normpath(output_path)

        qs = Contato.objects.select_related('colaborador_responsavel').order_by('razao_social')
        wb = gerar_workbook_contatos(qs)
        wb.save(output_path)

        self.stdout.write(self.style.SUCCESS(
            f'{qs.count()} contatos exportados para: {output_path}'
        ))
