from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimestampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Review(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    project = models.CharField(max_length=255)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    helpful = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        default_manager_name = 'objects'

    def __str__(self):
        return f"Review by {self.user.name} for {self.project}"

    @property
    def reviewer_name(self):
        return self.user.name if self.user else ''

class HelpfulMark(TimestampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_marks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['review', 'user']

@receiver(post_save, sender=Review)
def update_leaderboard_stats(sender, instance, created, **kwargs):
    from leaderboards.models import LeaderboardStats
    
    # Update only reviewer's stats
    reviewer_stats, _ = LeaderboardStats.objects.get_or_create(user=instance.user)
    reviewer_stats.update_stats()
