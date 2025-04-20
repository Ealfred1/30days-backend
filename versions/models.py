from django.db import models
from core.models import TimestampedModel

# Create your models here.

class Version(TimestampedModel):
    name = models.CharField(max_length=100)  # e.g., "Kairos"
    number = models.IntegerField()  # e.g., 7
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-number']

    def __str__(self):
        return f"v{self.number} - {self.name}"

    @property
    def participant_count(self):
        return self.submissions.values('user').distinct().count()

    @property
    def submission_count(self):
        return self.submissions.count()
