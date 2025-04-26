from rest_framework import serializers
from .models import Submission, Technology, SubmissionImage
from .utils import upload_image_to_cloudinary
from versions.models import Version
from django.utils import timezone
from django.db.models import Max

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
    additional_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
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

        # Get the user's latest submission day number or start from 1
        latest_submission = Submission.objects.filter(
            user=self.context['request'].user,
            version=active_version
        ).aggregate(Max('day_number'))
        
        current_day = latest_submission['day_number__max']
        if current_day is None:
            day_number = 1
        else:
            day_number = current_day + 1

        if day_number > 30:
            raise serializers.ValidationError("You have completed all 30 days of submissions")

        # Handle technologies
        technologies_data = validated_data.pop('technologies', [])
        additional_images = validated_data.pop('additional_images', [])
        preview_image_file = validated_data.pop('preview_image_file', None)

        # Add version and day number to validated data
        validated_data['version'] = active_version
        validated_data['day_number'] = day_number
        validated_data['user'] = self.context['request'].user

        # Handle main preview image
        if preview_image_file:
            upload_result = upload_image_to_cloudinary(preview_image_file)
            if upload_result:
                validated_data['preview_image'] = upload_result['secure_url']
                validated_data['cloudinary_public_id'] = upload_result['public_id']

        # Create submission
        submission = super().create(validated_data)

        # Add technologies
        for tech_name in technologies_data:
            tech, _ = Technology.objects.get_or_create(name=tech_name)
            submission.technologies.add(tech)

        # Handle additional images
        for image_file in additional_images:
            upload_result = upload_image_to_cloudinary(image_file)
            if upload_result:
                SubmissionImage.objects.create(
                    submission=submission,
                    image_url=upload_result['secure_url'],
                    cloudinary_public_id=upload_result['public_id']
                )

        return submission

    def validate_repository_url(self, value):
        """
        Validate repository URL format
        """
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        return value 

class SubmissionDetailSerializer(serializers.ModelSerializer):
    technologies = serializers.SerializerMethodField()
    additional_images = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            'id', 'title', 'description', 'repository_url', 'live_demo_url',
            'preview_image', 'day_number', 'technologies', 'additional_images',
            'created_at', 'updated_at', 'user', 'branch'
        ]

    def get_technologies(self, obj):
        return [tech.name for tech in obj.technologies.all()]

    def get_additional_images(self, obj):
        return [img.image_url for img in obj.images.all()]

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.name,
            'avatar': obj.user.avatar
        } 