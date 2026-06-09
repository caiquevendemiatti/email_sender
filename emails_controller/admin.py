import io
from django.contrib import admin, messages
from django.http import HttpResponse
from .models import Colaborador, Contato, Task_Envio, ConteudoEmail, GeradorTarefas, ImportacaoContatos
from .aux_files.contact_export import gerar_workbook_contatos
from .aux_files.contact_import import processar_importacao, formatar_resultado


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "habilitado")
    actions = ['create_new_address_task']

    def create_new_address_task(self, request, colaborators):
        for colaborator in colaborators:
            contact_list = Contato.objects.filter(ativo=True, excluido=False, colaborador_responsavel=colaborator)

            for contact in contact_list:
                task_envio = Task_Envio(
                    tarefa="Novo endereço",
                    assunto="Hidrotube em novo endereço",
                    contato=contact,
                    enviado=False
                )
                task_envio.save()


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "contato", "ativo", "excluido")
    readonly_fields = ('id',)
    list_filter = ("razao_social", )
    actions = ['create_new_address_task', 'exportar_planilha']

    def create_new_address_task(self, request, contacts):
        for contact in contacts:
            task_envio = Task_Envio(
                tarefa="Novo endereço",
                assunto="Hidrotube em novo endereço",
                contato=contact,
                enviado=False
            )
            task_envio.save()

    def exportar_planilha(self, request, queryset):
        qs = Contato.objects.select_related('colaborador_responsavel').order_by('razao_social')
        wb = gerar_workbook_contatos(qs)
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="contatos.xlsx"'
        return response

    exportar_planilha.short_description = 'Exportar planilha de contatos'


@admin.register(Task_Envio)
class TaskEnvioAdmin(admin.ModelAdmin):
    list_display = ("tarefa", "assunto", "contato", "enviado")


@admin.register(ConteudoEmail)
class ConteudoEmailAdmin(admin.ModelAdmin):
    list_display = ('assunto',)


@admin.register(GeradorTarefas)
class GeradorTarefasAdmin(admin.ModelAdmin):
    list_display = ('pk', 'conteudo_email', 'por_vendedor', 'vendedor', 'por_contato')


@admin.register(ImportacaoContatos)
class ImportacaoContatosAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'simulacao', 'status', 'data_importacao')
    readonly_fields = ('data_importacao', 'status', 'resultado')

    def get_fields(self, request, obj=None):
        if obj:
            return ('arquivo', 'simulacao', 'data_importacao', 'status', 'resultado')
        return ('arquivo', 'simulacao')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        try:
            obj.arquivo.open('rb')
            result = processar_importacao(obj.arquivo, dry_run=obj.simulacao)
            obj.arquivo.close()
        except Exception as e:
            obj.status = 'erro'
            obj.resultado = f'Erro ao processar arquivo: {e}'
            obj.save(update_fields=['status', 'resultado'])
            self.message_user(request, f'Erro ao processar: {e}', level=messages.ERROR)
            return

        obj.resultado = formatar_resultado(result, dry_run=obj.simulacao)
        error_count = len(result['errors'])

        if error_count == 0:
            obj.status = 'sucesso'
        elif result['updated'] > 0 or result['created'] > 0:
            obj.status = 'parcial'
        else:
            obj.status = 'erro'

        obj.save(update_fields=['status', 'resultado'])

        summary = (
            f'{"[SIMULAÇÃO] " if obj.simulacao else ""}'
            f'Criados: {result["created"]} | '
            f'Atualizados: {result["updated"]} | '
            f'Sem alterações: {result["skipped"]} | '
            f'Erros: {error_count}'
        )
        level = messages.WARNING if error_count else messages.SUCCESS
        self.message_user(request, summary, level=level)
