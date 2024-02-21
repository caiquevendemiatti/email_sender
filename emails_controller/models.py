from django.db import models
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import BooleanField


# Create your models here.
class Colaborador(models.Model):
    nome = models.CharField(max_length=600, blank=False)
    matricula = models.IntegerField(blank=True, null=True, default=None)
    habilitado = models.BooleanField(default=True)
    ddd = models.CharField(max_length=2, null=False, blank=False, default='19')
    whatsapp = models.CharField(max_length=12, null=False, blank=False, default='997898757')
    e_mail = models.EmailField(max_length=400, blank=False, null=False, unique=True)

    def __str__(self):
        return str(self.nome)

    def delete(self):
        self.enable = False
        self.save(update_fields=('enable',))


class Contato(models.Model):
    razao_social = models.CharField(max_length=255, blank=False, null=False)
    contato = models.CharField(max_length=255, blank=False, null=False)
    e_mail = models.EmailField(max_length=400, blank=False, null=False, unique=True)
    ativo = models.BooleanField(default=True, null=False, blank=False)
    excluido = models.BooleanField(default=False, null=False, blank=False)
    colaborador_responsavel = models.ForeignKey(Colaborador, on_delete=models.PROTECT)
    pesquisa_satisfacao = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return str(self.razao_social)


class ConteudoEmail(models.Model):
    assunto = models.CharField(max_length=255, blank=False, null=False)
    cabecalho = models.CharField(max_length=255, blank=False, null=False)
    rodape = models.CharField(max_length=255, blank=False, null=False)
    titulo = models.CharField(max_length=500, blank=False, null=False, default="'")
    conteudo_A = models.TextField(blank=False, null=False)
    conteudo_B = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(f"{self.assunto}")


class GeradorTarefas(models.Model):
    todos_contatos = models.BooleanField(default=False, null=False, blank=False)
    por_vendedor = models.BooleanField(default=True, null=False, blank=False)
    vendedor = models.ForeignKey(Colaborador, on_delete=models.PROTECT, null=True, blank=True)
    por_contato = models.BooleanField(default=False, null=False, blank=False)
    contato = models.IntegerField(null=True, blank=True)
    conteudo_email = models.ForeignKey(ConteudoEmail, on_delete=models.PROTECT)
    tarefas_criadas = models.BooleanField(default=False, null=False, blank=False)
    pesquisa_satisfacao = models.BooleanField(default=False, null=False, blank=False, verbose_name='Pesquisa de Satisfação')

    def clean(self):
        if not self.todos_contatos and not self.por_vendedor and not self.por_contato:
            raise ValidationError(_('Selecione apenas um filtro entre "Por Contato", '
                                    '"Por Vendedor" ou  "Todos os Contatos"'))

        if self.todos_contatos and self.por_vendedor:
            raise ValidationError(_('Selecione um filtro entre "Por Contato", "Por Vendedor" ou  "Todos os Contatos"'))

        if self.todos_contatos and self.por_contato:
            raise ValidationError(_('Selecione um filtro entre "Por Contato", "Por Vendedor" ou  "Todos os Contatos"'))

        if self.por_vendedor and self.por_contato:
            raise ValidationError(_('Selecione um filtro entre "Por Contato", "Por Vendedor" ou  "Todos os Contatos"'))

        if self.todos_contatos and (self.contato is not None or self.vendedor is not None):
            raise ValidationError(_('Não adicionar "Contato" ou "Vendedor" para o filtro "Todos os Contatos"'))

        if self.por_vendedor and (self.vendedor is None):
            raise ValidationError(_('Selecionar um vendedor'))

        if self.por_vendedor and (self.contato is not None):
            raise ValidationError(_('Não selecionar um "Contato" para o filtro "Por Vendedor"'))

        if self.por_contato and (self.contato is None):
            raise ValidationError(_('Selecionar um contato'))

        if self.por_contato and (self.vendedor is not None):
            raise ValidationError(_('Não selecionar um "Vendedor" para o filtro "Por Contato"'))

    def save(self, *args, **kwargs):

        if self.tarefas_criadas:
            super().save(*args, **kwargs)
            return

        self.tarefas_criadas = True

        if self.todos_contatos:
            super().save(*args, **kwargs)
            self.create_task_all_contacts()
            return

        if self.por_vendedor:
            super().save(*args, **kwargs)
            self.create_task_by_vendor()

        if self.por_contato:
            super().save(*args, **kwargs)
            self.create_task_by_contact()
            return

    def create_task_all_contacts(self):
        contacts = Contato.objects.filter(ativo=True, excluido=False)
        if self.pesquisa_satisfacao:
            contacts = contacts.filter(pesquisa_satisfacao=True)

        for contact in contacts:
            task_envio = Task_Envio(
                tarefa=self.pk,
                assunto=self.conteudo_email.assunto,
                contato=contact,
                conteudo=self.conteudo_email,
                enviado=False
            )
            task_envio.save()

    def create_task_by_vendor(self):
        contacts = Contato.objects.filter(ativo=True, excluido=False, colaborador_responsavel=self.vendedor)
        if self.pesquisa_satisfacao:
            contacts = contacts.filter(pesquisa_satisfacao=True)

        for contact in contacts:
            task_envio = Task_Envio(
                tarefa=self.pk,
                assunto=self.conteudo_email.assunto,
                contato=contact,
                conteudo=self.conteudo_email,
                enviado=False
            )
            task_envio.save()

    def create_task_by_contact(self):
        contacts = Contato.objects.get(pk=self.contato)
        if self.pesquisa_satisfacao:
            contacts = contacts.filter(pesquisa_satisfacao=True)

        task_envio = Task_Envio(
            tarefa=self.pk,
            assunto=self.conteudo_email.assunto,
            contato=contacts,
            conteudo=self.conteudo_email,
            enviado=False
        )
        task_envio.save()


class Task_Envio(models.Model):
    tarefa = models.CharField(max_length=255, blank=False, null=False)
    assunto = models.CharField(max_length=255, blank=False, null=False)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE)
    enviado = models.BooleanField(default=False)
    tentativas_envio = models.IntegerField(default=0)
    conteudo = models.ForeignKey(ConteudoEmail, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(f"Tarefa: {self.tarefa} - Assunto: {self.assunto}")
