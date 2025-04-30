from rest_framework import serializers
from .models import Review, HelpfulMark
from users.serializers import UserDetailSerializer

class ReviewSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    reviewer_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 
            'user', 
            'user_id',
            'reviewer_name',
            'project', 
            'rating', 
            'comment', 
            'created_at',
            'helpful'
        ]
        read_only_fields = ['created_at', 'helpful']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        if user_id:
            validated_data['user_id'] = user_id
        return super().create(validated_data)

class HelpfulMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpfulMark
        fields = '__all__'
        read_only_fields = ('user',) 