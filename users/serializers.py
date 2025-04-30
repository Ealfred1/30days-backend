from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from core.models import Activity
from .models import User, PointsAdjustment

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = (
            'id', 'email', 'name', 'avatar', 'firebase_uid', 
            'provider', 'date_joined', 'last_login',
            'is_staff', 'is_superuser'
        )
        read_only_fields = ['email', 'firebase_uid', 'provider', 'date_joined', 'last_login']

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(required=True)
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'avatar', 'provider')
        read_only_fields = ('email', 'provider')

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class PointsAdjustmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    adjusted_by = serializers.StringRelatedField()
    
    class Meta:
        model = PointsAdjustment
        fields = '__all__' 