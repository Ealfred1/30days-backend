from rest_framework import serializers
from .models import Review, HelpfulMark

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.name', read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('reviewer', 'helpful_count')

class HelpfulMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpfulMark
        fields = '__all__'
        read_only_fields = ('user',) 