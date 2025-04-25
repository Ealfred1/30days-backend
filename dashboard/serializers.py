from rest_framework import serializers
from .models import Activity
from versions.models import Version
from submissions.models import Submission
from users.serializers import UserSerializer

class ActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Activity
        fields = '__all__'

class DashboardStatsSerializer(serializers.Serializer):
    days_remaining = serializers.IntegerField()
    days_completed = serializers.IntegerField()
    submission_count = serializers.IntegerField()
    last_submission_date = serializers.DateTimeField()
    rank = serializers.IntegerField()
    rank_percentile = serializers.FloatField()
    total_participants = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    timeline = serializers.ListField()
    recent_activities = ActivitySerializer(many=True) 