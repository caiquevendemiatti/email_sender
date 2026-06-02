from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails_controller', '0018_add_padrao_a_email_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='conteudoemail',
            name='preheader',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Texto de preview (preheader)'),
        ),
    ]
