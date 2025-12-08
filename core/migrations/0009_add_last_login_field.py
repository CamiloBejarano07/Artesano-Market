from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_auth_user_fields'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL forward - agregar columna last_login
            sql="ALTER TABLE personas ADD COLUMN last_login DATETIME NULL;",
            # SQL backward - eliminar columna si existe
            reverse_sql="ALTER TABLE personas DROP COLUMN last_login;",
        ),
    ]
