# Generated migration for Pago estado change

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_producto_activo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pago',
            name='estado',
            field=models.CharField(
                choices=[
                    ('procesando', 'Procesando'),
                    ('completado', 'Completado'),
                    ('fallido', 'Fallido')
                ],
                default='procesando',
                max_length=20
            ),
        ),
    ]
