from django.db import models

# Create your models here.

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Activity(TimestampedModel):
    ACTIVITY_TYPES = (
        ('submission', 'Submitted Project'),
        ('review', 'Reviewed Project'),
        ('rating', 'Rated Project'),
    )
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    submission = models.ForeignKey('submissions.Submission', on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey('reviews.Review', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'activities'

    def __str__(self):
        return f"{self.user.name} {self.get_activity_type_display()}"