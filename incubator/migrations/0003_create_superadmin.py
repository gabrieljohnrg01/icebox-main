# Generated migration to create default superadmin

from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_superadmin(apps, schema_editor):
    User = apps.get_model('incubator', 'User')
    
    # Check if superadmin already exists
    if not User.objects.filter(username='superadmin').exists():
        User.objects.create(
            username='superadmin',
            email='superadmin@localhost',
            password=make_password('123'),
            first_name='Super',
            last_name='Admin',
            role='super_admin',
            is_staff=True,
            is_superuser=True,
        )


def reverse_superadmin(apps, schema_editor):
    User = apps.get_model('incubator', 'User')
    User.objects.filter(username='superadmin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('incubator', '0002_user_middle_name'),
    ]

    operations = [
        migrations.RunPython(create_superadmin, reverse_superadmin),
    ]
