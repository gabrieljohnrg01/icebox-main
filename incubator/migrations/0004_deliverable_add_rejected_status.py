# Generated migration to add 'rejected' status to Deliverable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incubator', '0003_create_superadmin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverable',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='pending',
                max_length=20
            ),
        ),
    ]
