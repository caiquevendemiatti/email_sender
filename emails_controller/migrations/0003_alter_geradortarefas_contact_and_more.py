# Generated by Django 4.1.6 on 2023-03-23 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emails_controller', '0002_conteudoemail_geradortarefas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geradortarefas',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='emails_controller.contato'),
        ),
        migrations.AlterField(
            model_name='geradortarefas',
            name='vendedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='emails_controller.colaborador'),
        ),
    ]
