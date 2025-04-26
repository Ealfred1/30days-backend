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
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.CharField(source='user.avatar', allow_null=True)
    badges = UserBadgeSerializer(source='user.badges', many=True, read_only=True)
    rank = serializers.IntegerField(read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, coerce_to_string=False)

    def get_user_name(self, obj):
        # Get the name from the user model
        name = obj.user.name
        
        if not name:
            # Fallback to email if no name is set
            return obj.user.email.split('@')[0]
            
        # If name exists, return it directly since it should already be the full name
        # from Firebase (e.g. "Eric Alfred")
        return name

    class Meta:
        model = LeaderboardStats
        fields = [
            'id', 'user_name', 'user_avatar', 'points', 'current_streak',
            'longest_streak', 'submissions_count', 'average_rating',
            'reviews_given_count', 'reviews_received_count',
            'helpful_marks_received', 'rank', 'badges'
        ]