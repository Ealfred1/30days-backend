from django.db import models
from django.conf import settings
from core.models import TimestampedModel

# Create your models here.

class Technology(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Submission(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    version = models.ForeignKey('versions.Version', on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    repository_url = models.URLField()
    live_demo_url = models.URLField(blank=True)
    branch = models.CharField(max_length=100, default='main')
    technologies = models.ManyToManyField(Technology)
    day_number = models.IntegerField()
    
    # Media
    preview_image = models.URLField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'version', 'day_number']

    def __str__(self):
        return f"{self.title} by {self.user.name}"

class SubmissionImage(TimestampedModel):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    
    def __str__(self):
        return f"Image for {self.submission.title}"
