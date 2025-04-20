from rest_framework import serializers
from .models import Submission, Technology, SubmissionImage

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = '__all__'

class SubmissionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionImage
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)
    images = SubmissionImageSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ('user',)

    def create(self, validated_data):
        technologies_data = validated_data.pop('technologies')
        submission = Submission.objects.create(**validated_data)
        
        for tech_data in technologies_data:
            tech, _ = Technology.objects.get_or_create(**tech_data)
            submission.technologies.add(tech)
        
        return submission 