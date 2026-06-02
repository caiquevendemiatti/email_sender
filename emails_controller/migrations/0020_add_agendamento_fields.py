from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails_controller', '0019_conteudoemail_preheader'),
    ]

    operations = [
        migrations.AddField(
            model_name='geradortarefas',
            name='data_hora_agendamento',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Agendamento'),
        ),
        migrations.AddField(
            model_name='task_envio',
            name='data_hora_agendamento',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Agendamento'),
        ),
    ]
