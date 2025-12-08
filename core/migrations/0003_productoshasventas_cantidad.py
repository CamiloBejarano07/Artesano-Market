# Generated migration for adding cantidad field to ProductosHasVentas

from django.db import migrations, models


def set_default_cantidad(apps, schema_editor):
    """Establecer cantidad = 1 para todos los registros existentes"""
    ProductosHasVentas = apps.get_model('core', 'ProductosHasVentas')
    ProductosHasVentas.objects.filter(cantidad__isnull=True).update(cantidad=1)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_personas_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='productoshasventas',
            name='cantidad',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.RunPython(set_default_cantidad),
    ]

