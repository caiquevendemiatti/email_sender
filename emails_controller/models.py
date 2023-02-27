from django.db import models
import logging
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


class Task_Envio(models.Model):
    tarefa = models.CharField(max_length=255, blank=False, null=False)
    assunto = models.CharField(max_length=255, blank=False, null=False)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE)
    enviado = models.BooleanField(default=False)
    tentativas_envio = models.IntegerField(default=0)

    def __str__(self):
        return str(f"Tarefa: {self.tarefa} - Assunto: {self.assunto}")
