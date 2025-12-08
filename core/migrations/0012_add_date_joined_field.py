from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_add_is_superuser_field'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL forward - agregar columna date_joined si no existe
            sql="ALTER TABLE personas ADD COLUMN date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;",
            # SQL backward - eliminar columna
            reverse_sql="ALTER TABLE personas DROP COLUMN date_joined;",
        ),
    ]
