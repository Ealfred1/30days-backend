from rest_framework import serializers
from .models import Badge, UserBadge, LeaderboardStats

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class UserBadgeSerializer(serializers.ModelSerializer):
    badge_details = BadgeSerializer(source='badge', read_only=True)

    class Meta:
        model = UserBadge
        fields = ['id', 'earned_at', 'badge_details']

class LeaderboardStatsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    badges = UserBadgeSerializer(source='user.badges', many=True, read_only=True)
    rank = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaderboardStats
        fields = [
            'id', 'user_name', 'user_avatar', 'points', 'current_streak',
            'longest_streak', 'submissions_count', 'average_rating',
            'reviews_given_count', 'reviews_received_count',
            'helpful_marks_received', 'rank', 'badges'
        ] 