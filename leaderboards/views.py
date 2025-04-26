from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import LeaderboardStats, Badge, UserBadge
from .serializers import LeaderboardStatsSerializer, BadgeSerializer
from drf_spectacular.utils import extend_schema
from submissions.models import Submission

# Create your views here.

@extend_schema(tags=['leaderboards'])
class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaderboardStatsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Ensure every user has stats
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Create stats for users who don't have them
        for user in User.objects.all():
            stats, created = LeaderboardStats.objects.get_or_create(user=user)
            if created or True:  # Always update to ensure fresh data
                stats.update_stats()
        
        return LeaderboardStats.objects.all().order_by('-points')

    @action(detail=False)
    def overview(self, request):
        """Get overview statistics for the leaderboard"""
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        # Current stats
        current_stats = {
            'total_submissions': Submission.objects.count(),
            'active_participants': LeaderboardStats.objects.filter(submissions_count__gt=0).count(),
            'average_rating': LeaderboardStats.objects.filter(average_rating__gt=0).aggregate(avg=Avg('average_rating'))['avg'] or 0
        }
        
        # Last week's stats for comparison
        last_week_submissions = Submission.objects.filter(created_at__lte=week_ago).count()
        last_week_participants = LeaderboardStats.objects.filter(
            submissions_count__gt=0,
            user__submission__created_at__lte=week_ago
        ).distinct().count()
        last_week_rating = LeaderboardStats.objects.filter(
            average_rating__gt=0
        ).aggregate(avg=Avg('average_rating'))['avg'] or 0

        # Calculate weekly changes
        submissions_change = ((current_stats['total_submissions'] - last_week_submissions) / max(last_week_submissions, 1)) * 100
        participants_change = ((current_stats['active_participants'] - last_week_participants) / max(last_week_participants, 1)) * 100
        rating_change = current_stats['average_rating'] - last_week_rating

        return Response({
            'total_submissions': current_stats['total_submissions'],
            'active_participants': current_stats['active_participants'],
            'average_rating': round(current_stats['average_rating'], 1),
            'weekly_change': {
                'submissions': round(submissions_change, 1),
                'participants': round(participants_change, 1),
                'rating': round(rating_change, 2)
            }
        })

    @action(detail=False)
    def my_stats(self, request):
        """Get current user's leaderboard stats"""
        stats = LeaderboardStats.objects.get(user=request.user)
        return Response(self.get_serializer(stats).data)
