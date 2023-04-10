from django.db import models
import logging

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

    def save(self, *args, **kwargs):
        if not self.tarefas_criadas:

            if self.todos_contatos:
                if self.por_vendedor and self.por_contato:
                    raise Exception("Marcar apenas uma opção de geração de task")
                    return

                super().save(*args, **kwargs)
                self.create_task_all_contacts()
                return

            if self.por_vendedor:
                if self.todos_contatos and self.por_contato:
                    raise Exception("Marcar apenas uma opção de geração de task")
                    return
                if not self.vendedor:
                    raise Exception("O campo vendedor deve ser preenchido")
                    return
                super().save(*args, **kwargs)
                self.create_task_by_vendor()
                return

            if self.por_contato:
                if self.todos_contatos and self.por_vendedor:
                    raise Exception("Marcar apenas uma opção de geração de task")
                    return
                if not self.contato:
                    raise Exception("O campo contato deve ser preenchido")
                    return
                super().save(*args, **kwargs)
                self.create_task_by_contact()
                return

        super().save(*args, **kwargs)
        return

    def create_task_all_contacts(self):
        contacts = Contato.objects.filter(ativo=True, excluido=False)
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
        contact = Contato.objects.get(pk=self.contato)

        task_envio = Task_Envio(
            tarefa=self.pk,
            assunto=self.conteudo_email.assunto,
            contato=contact,
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
