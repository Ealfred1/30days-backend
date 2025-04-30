from django.db import models
from django.conf import settings
from django.db.models import Avg, Count, Sum
from core.models import TimestampedModel

# Create your models here.

class Badge(TimestampedModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # For storing icon name/class
    criteria_count = models.IntegerField(default=0)  # Number required to earn badge
    criteria_type = models.CharField(max_length=50)  # e.g., 'submissions', 'reviews', 'rating'

    def __str__(self):
        return self.name

class UserBadge(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']

class LeaderboardStats(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaderboard_stats')
    points = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    submissions_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_given_count = models.IntegerField(default=0)
    reviews_received_count = models.IntegerField(default=0)
    helpful_marks_received = models.IntegerField(default=0)

    class Meta:
        ordering = ['-points', '-current_streak', '-average_rating']

    @property
    def rank(self):
        return LeaderboardStats.objects.filter(points__gt=self.points).count() + 1

    def update_stats(self):
        """Update user's leaderboard statistics"""
        from reviews.models import Review

        # Update review stats
        reviews_given = Review.objects.filter(user=self.user)
        self.reviews_given_count = reviews_given.count()
        
        # Update helpful marks
        self.helpful_marks_received = reviews_given.aggregate(
            total_helpful=Sum('helpful')
        )['total_helpful'] or 0

        # Calculate points based on reviews and helpful marks
        self.points = (
            self.reviews_given_count * 10 +  # Points for giving reviews
            self.helpful_marks_received * 5   # Points for receiving helpful marks
        )

        self.save()
