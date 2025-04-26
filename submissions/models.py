from django.db import models
from django.conf import settings
from core.models import TimestampedModel
from .utils import delete_image_from_cloudinary

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
    technologies = models.ManyToManyField('Technology')
    day_number = models.IntegerField()
    
    # Media
    preview_image = models.URLField(blank=True)
    cloudinary_public_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'version', 'day_number']

    def __str__(self):
        return f"{self.title} by {self.user.name}"

    def delete(self, *args, **kwargs):
        # Delete image from Cloudinary before deleting the submission
        if self.cloudinary_public_id:
            delete_image_from_cloudinary(self.cloudinary_public_id)
        super().delete(*args, **kwargs)

    @property
    def additional_images(self):
        return self.images.all()

class SubmissionImage(models.Model):
    submission = models.ForeignKey(
        Submission, 
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField()
    cloudinary_public_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.submission.title}"
