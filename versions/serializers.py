from rest_framework import serializers
from .models import Version

class VersionSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Version
        fields = [
            'id',
            'name',
            'number',
            'start_date',
            'end_date',
            'description',
            'is_active',
            'participant_count',
            'submission_count',
            'created_at',
            'updated_at'
        ] 