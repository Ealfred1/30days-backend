from rest_framework import serializers
from .models import Review, HelpfulMark
from users.serializers import UserDetailSerializer

class ReviewSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'project',
            'rating',
            'comment',
            'helpful',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'helpful', 'created_at']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_project(self, value):
        """Validate project name"""
        if not value.strip():
            raise serializers.ValidationError("Project name cannot be empty")
        return value

    def validate_comment(self, value):
        """Validate comment"""
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty")
        return value

class HelpfulMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpfulMark
        fields = '__all__'
        read_only_fields = ('user',) 