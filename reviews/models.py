from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimestampedModel

# Create your models here.

class Review(TimestampedModel):
    submission = models.ForeignKey('submissions.Submission', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    helpful_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['submission', 'reviewer']

    def __str__(self):
        return f"Review by {self.reviewer.name} on {self.submission.title}"

class HelpfulMark(TimestampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_marks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['review', 'user']
