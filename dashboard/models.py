from django.db import models
from core.models import TimestampedModel
from django.conf import settings

# Create your models here.

class Activity(TimestampedModel):
    ACTIVITY_TYPES = (
        ('submission', 'Submission'),
        ('review', 'Review'),
        ('rating', 'Rating'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    related_submission = models.ForeignKey(
        'submissions.Submission', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='dashboard_activities'
    )
    related_review = models.ForeignKey(
        'reviews.Review', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='dashboard_activities'
    )
    
    class Meta:
        app_label = 'dashboard'
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
