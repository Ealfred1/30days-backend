from rest_framework import serializers
from .models import Version

class VersionSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    technologies = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )
    
    class Meta:
        model = Version
        fields = [
            'id',
            'name',
            'number',
            'codename',
            'description',
            'start_date',
            'end_date',
            'is_active',
            'focus_area',
            'technologies',
            'participant_count',
            'submission_count',
            'status',
            'days_remaining',
            'progress_percentage',
            'created_at',
            'updated_at'
        ]

class VersionComparisonSerializer(serializers.Serializer):
    version1 = VersionSerializer()
    version2 = VersionSerializer()
    participant_difference = serializers.IntegerField()
    submission_difference = serializers.IntegerField()
    technology_overlap = serializers.ListField(child=serializers.CharField()) 