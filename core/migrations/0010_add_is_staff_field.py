from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_add_last_login_field'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL forward - agregar columna is_staff
            sql="ALTER TABLE personas ADD COLUMN is_staff BOOLEAN NOT NULL DEFAULT 0;",
            # SQL backward - eliminar columna
            reverse_sql="ALTER TABLE personas DROP COLUMN is_staff;",
        ),
    ]
