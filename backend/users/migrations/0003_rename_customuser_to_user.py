from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_follow'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomUser',
            new_name='User',
        ),
        migrations.AlterModelTable(
            name='user',
            table='users_customuser',
        ),
    ]
