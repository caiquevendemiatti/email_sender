from django.contrib import admin
from .models import Colaborador, Contato, Task_Envio, ConteudoEmail, GeradorTarefas

# Register your models here.
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
    actions = ['create_new_address_task']

    def create_new_address_task(self, request, contacts):

       for contact in contacts:
           task_envio = Task_Envio(
               tarefa="Novo endereço",
               assunto="Hidrotube em novo endereço",
               contato=contact,
               enviado=False
           )
           task_envio.save()


@admin.register(Task_Envio)
class TaskEnvioAdmin(admin.ModelAdmin):
    list_display = ("tarefa", "assunto", "contato", "enviado")


@admin.register(ConteudoEmail)
class ConteudoEmailAdmin(admin.ModelAdmin):
    list_display = ('assunto',)


@admin.register(GeradorTarefas)
class GeradorTarefasAdmin(admin.ModelAdmin):
    list_display = ('pk','conteudo_email', 'por_vendedor', 'vendedor', 'por_contato')