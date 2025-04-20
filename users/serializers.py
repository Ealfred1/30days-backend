from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from core.models import Activity

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(required=True)
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'avatar', 'bio', 'github_username', 
                 'country', 'points', 'streak')
        read_only_fields = ('points', 'streak')

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__' 