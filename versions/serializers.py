from rest_framework import serializers
from .models import Version

class VersionSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Version
        fields = '__all__' 