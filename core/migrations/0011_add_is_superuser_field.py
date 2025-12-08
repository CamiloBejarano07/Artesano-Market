from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_is_staff_field'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL forward - agregar columna is_superuser
            sql="ALTER TABLE personas ADD COLUMN is_superuser BOOLEAN NOT NULL DEFAULT 0;",
            # SQL backward - eliminar columna
            reverse_sql="ALTER TABLE personas DROP COLUMN is_superuser;",
        ),
    ]
