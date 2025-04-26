from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimestampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver

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

@receiver(post_save, sender=Review)
def update_leaderboard_stats(sender, instance, created, **kwargs):
    from leaderboards.models import LeaderboardStats
    
    # Update reviewer's stats
    reviewer_stats, _ = LeaderboardStats.objects.get_or_create(user=instance.reviewer)
    reviewer_stats.update_stats()
    
    # Update submission owner's stats
    owner_stats, _ = LeaderboardStats.objects.get_or_create(user=instance.submission.user)
    owner_stats.update_stats()
