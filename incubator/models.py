from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('incubatee', 'Incubatee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='incubatee')
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

class Startup(models.Model):
    STAGE_CHOICES = (
        ('ideation', 'Ideation'),
        ('validation', 'Validation'),
        ('scaling', 'Scaling'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='startup_logos/', blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='ideation')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_startups')
    email = models.EmailField(max_length=120, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    members = models.ManyToManyField(User, through='StartupMember', related_name='startups')

    @property
    def progress(self):
        total = self.milestones.count()
        if total == 0:
            return 0
        completed = self.milestones.filter(status='completed').count()
        return int((completed / total) * 100)

    def __str__(self):
        return self.name

class StartupMember(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True, null=True)  # e.g., CEO, CTO
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.startup.name}"

class Milestone(models.Model):
    STATUS_CHOICES = (
        ('not-yet', 'Not Yet'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='milestones')
    milestone_progress = models.IntegerField(blank=True, null=True) # Could be an index
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-yet')
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def is_locked(self):
        """Check if this milestone is locked (previous milestone not completed)"""
        if self.milestone_progress == 1:
            return False  # First milestone is never locked
        
        previous_milestone = self.startup.milestones.filter(
            milestone_progress=self.milestone_progress - 1
        ).first()
        
        if previous_milestone:
            return previous_milestone.status != 'completed'
        return False

    def __str__(self):
        return f"{self.startup.name} - Milestone {self.milestone_progress}"

class Deliverable(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='deliverables')
    name = models.CharField(max_length=200)
    upload_file = models.FileField(upload_to='deliverables/', blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Readiness(models.Model):
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='readiness_levels')
    name = models.CharField(max_length=200)
    level = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username}"

class ProgressReport(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='progress_reports')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievements = models.TextField(blank=True, null=True)
    challenges = models.TextField(blank=True, null=True)
    next_steps = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
