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
        return Response({
            'days_remaining': 30,
            'days_completed': 0,
            'submission_count': 0,
            'last_submission_date': None,
            'rank': 0,
            'rank_percentile': 0,
            'total_participants': 0,
            'progress_percentage': 0,
            'timeline': [{'day': i + 1, 'completed': False} for i in range(30)],
            'recent_activities': []
        })
    
    # Calculate days
    today = timezone.now().date()
    total_days = (active_version.end_date - active_version.start_date).days
    days_elapsed = (today - active_version.start_date).days
    days_remaining = max(0, total_days - days_elapsed)
    days_completed = min(total_days, max(0, days_elapsed))
    
    # Get user submissions
    user_submissions = Submission.objects.filter(
        user=request.user,
        version=active_version
    )
    
    # Get submission days
    completed_days = set(user_submissions.values_list('day_number', flat=True))
    
    # Calculate timeline
    timeline = [
        {
            'day': day + 1,
            'completed': (day + 1) in completed_days,
            'current': (day + 1) == days_completed + 1
        }
        for day in range(30)
    ]
    
    # Calculate rank and participants
    users_with_submissions = Submission.objects.filter(
        version=active_version
    ).values('user').annotate(
        count=Count('id')
    ).order_by('-count')
    
    total_participants = users_with_submissions.count()
    user_rank = 1
    
    for i, user_stats in enumerate(users_with_submissions):
        if user_stats['user'] == request.user.id:
            user_rank = i + 1
            break
    
    # Calculate progress
    progress_percentage = (days_completed / 30) * 100 if days_completed > 0 else 0
    
    # Get recent activities
    recent_activities = Activity.objects.select_related(
        'user'
    ).order_by('-created_at')[:10]
    
    data = {
        'days_remaining': days_remaining,
        'days_completed': days_completed,
        'submission_count': user_submissions.count(),
        'last_submission_date': user_submissions.first().created_at if user_submissions.exists() else None,
        'rank': user_rank,
        'rank_percentile': (user_rank / total_participants * 100) if total_participants > 0 else 0,
        'total_participants': total_participants,
        'progress_percentage': progress_percentage,
        'timeline': timeline,
        'recent_activities': recent_activities
    }
    
    return Response(data)

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
