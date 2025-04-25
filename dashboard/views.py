from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import Activity
from .serializers import DashboardStatsSerializer, ActivitySerializer
from versions.models import Version
from submissions.models import Submission
from users.serializers import UserSerializer
from users.models import User

# Create your views here.

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    # Get active version
    active_version = Version.objects.filter(is_active=True).first()
    if not active_version:
        return Response({'error': 'No active version found'}, status=400)
    
    # Calculate days remaining and completed
    today = timezone.now().date()
    days_remaining = (active_version.end_date - today).days
    days_completed = 30 - days_remaining
    
    # Get user submissions
    user_submissions = Submission.objects.filter(
        user=request.user,
        version=active_version
    )
    
    # Calculate rank
    users_by_points = User.objects.annotate(
        total_points=Count('submissions', filter=Q(submissions__version=active_version))
    ).order_by('-total_points')
    
    user_rank = list(users_by_points).index(request.user) + 1
    total_participants = users_by_points.count()
    rank_percentile = (user_rank / total_participants) * 100
    
    # Get timeline
    timeline = [
        {
            'day': day,
            'completed': user_submissions.filter(day_number=day).exists()
        }
        for day in range(1, 31)
    ]
    
    # Get recent activities
    recent_activities = Activity.objects.select_related('user').order_by('-created_at')[:10]
    
    data = {
        'days_remaining': days_remaining,
        'days_completed': days_completed,
        'submission_count': user_submissions.count(),
        'last_submission_date': user_submissions.first().created_at if user_submissions.exists() else None,
        'rank': user_rank,
        'rank_percentile': rank_percentile,
        'total_participants': total_participants,
        'progress_percentage': (days_completed / 30) * 100,
        'timeline': timeline,
        'recent_activities': recent_activities
    }
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def leaderboard(request):
    active_version = Version.objects.filter(is_active=True).first()
    if not active_version:
        return Response({'error': 'No active version found'}, status=400)
    
    users = User.objects.annotate(
        submission_count=Count('submissions', filter=Q(submissions__version=active_version))
    ).order_by('-submission_count')[:100]
    
    return Response(UserSerializer(users, many=True).data)
