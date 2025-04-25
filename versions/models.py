from django.db import models
from core.models import TimestampedModel

# Create your models here.

class Version(TimestampedModel):
    name = models.CharField(max_length=255)
    number = models.IntegerField()  # This is the required field causing the error
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (v{self.number})"

    @property
    def participant_count(self):
        return self.submissions.values('user').distinct().count()

    @property
    def submission_count(self):
        return self.submissions.count()
