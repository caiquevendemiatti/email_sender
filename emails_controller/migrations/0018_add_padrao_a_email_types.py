from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails_controller', '0017_add_apresentacao_email_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conteudoemail',
            name='tipo_email',
            field=models.CharField(
                choices=[
                    ('6_fotos', '6 Fotos'),
                    ('sem_foto', 'Sem Fotos'),
                    ('apresentacao', 'Apresentação'),
                    ('padrao_a_4', 'Padrão A - 4 Fotos'),
                    ('padrao_a_6', 'Padrão A - 6 Fotos'),
                ],
                default='6_fotos',
                max_length=20,
            ),
        ),
    ]
