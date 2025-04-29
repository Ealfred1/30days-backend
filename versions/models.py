from django.db import models
from django.utils import timezone
from core.models import TimestampedModel

# Create your models here.

class Version(TimestampedModel):
    name = models.CharField(max_length=255)
    number = models.IntegerField(unique=True)
    codename = models.CharField(max_length=100, blank=True)  # e.g., "Kairos", "Chronos"
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    focus_area = models.CharField(max_length=255, blank=True)  # e.g., "UI/UX design"
    technologies = models.JSONField(default=list, blank=True)  # List of technologies used
    
    class Meta:
        ordering = ['-number']

    def __str__(self):
        return f"{self.name} (v{self.number}) - {self.codename}"

    @property
    def participant_count(self):
        return self.submissions.values('user').distinct().count()

    @property
    def submission_count(self):
        return self.submissions.count()

    @property
    def status(self):
        today = timezone.now().date()
        if today < self.start_date:
            return 'upcoming'
        elif today <= self.end_date:
            return 'active'
        else:
            return 'completed'

    @property
    def days_remaining(self):
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

    @property
    def progress_percentage(self):
        total_days = (self.end_date - self.start_date).days
        days_passed = (timezone.now().date() - self.start_date).days
        if days_passed < 0:
            return 0
        if days_passed > total_days:
            return 100
        return int((days_passed / total_days) * 100)
