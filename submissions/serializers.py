from rest_framework import serializers
from .models import Submission, Technology, SubmissionImage
from .utils import upload_image_to_cloudinary
from versions.models import Version
from django.utils import timezone

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = '__all__'

class SubmissionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionImage
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    preview_image_file = serializers.ImageField(write_only=True, required=False)
    technologies = serializers.ListField(child=serializers.CharField(), write_only=True)
    images = SubmissionImageSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ('user', 'preview_image', 'cloudinary_public_id', 'version', 'day_number')

    def create(self, validated_data):
        # Get current active version
        active_version = Version.objects.filter(is_active=True).first()
        if not active_version:
            raise serializers.ValidationError("No active challenge version found")

        # Calculate current day number
        start_date = active_version.start_date
        today = timezone.now().date()
        day_number = (today - start_date).days + 1

        if day_number < 1 or day_number > 30:
            raise serializers.ValidationError("Submissions are only allowed during the challenge period")

        # Handle technologies
        technologies_data = validated_data.pop('technologies', [])
        
        # Handle image upload
        preview_image_file = validated_data.pop('preview_image_file', None)
        if preview_image_file:
            upload_result = upload_image_to_cloudinary(preview_image_file)
            if upload_result:
                validated_data['preview_image'] = upload_result.get('secure_url')
                validated_data['cloudinary_public_id'] = upload_result.get('public_id')

        # Add version and day number
        validated_data['version'] = active_version
        validated_data['day_number'] = day_number

        # Create submission
        submission = Submission.objects.create(**validated_data)
        
        # Add technologies
        for tech_name in technologies_data:
            tech, _ = Technology.objects.get_or_create(name=tech_name)
            submission.technologies.add(tech)

        # Handle additional images
        additional_images = self.context['request'].FILES.getlist('additional_images[]')
        for image in additional_images:
            upload_result = upload_image_to_cloudinary(image)
            if upload_result:
                SubmissionImage.objects.create(
                    submission=submission,
                    image_url=upload_result.get('secure_url')
                )
        
        return submission

    def validate_repository_url(self, value):
        """
        Validate repository URL format
        """
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        return value 