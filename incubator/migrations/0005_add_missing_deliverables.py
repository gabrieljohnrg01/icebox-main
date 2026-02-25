# Generated migration to add missing deliverables to milestones

from django.db import migrations


def add_missing_deliverables(apps, schema_editor):
    Milestone = apps.get_model('incubator', 'Milestone')
    Deliverable = apps.get_model('incubator', 'Deliverable')
    
    deliverable_counts = {1: 5, 2: 3, 3: 4, 4: 3}
    
    # For each milestone, ensure it has the correct number of deliverables
    for milestone in Milestone.objects.all():
        current_count = milestone.deliverables.count()
        target_count = deliverable_counts.get(milestone.milestone_progress, 0)
        
        # If milestone has no deliverables, create them
        if current_count == 0 and target_count > 0:
            for j in range(1, target_count + 1):
                Deliverable.objects.create(
                    milestone=milestone,
                    name=f"Deliverable {j}",
                    requirements=f"Complete deliverable {j} for milestone {milestone.milestone_progress}",
                    status='pending'
                )


def reverse_add_deliverables(apps, schema_editor):
    # Reverse function - could delete but keeping for safety
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('incubator', '0004_deliverable_add_rejected_status'),
    ]

    operations = [
        migrations.RunPython(add_missing_deliverables, reverse_add_deliverables),
    ]
