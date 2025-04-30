from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from reviews.models import Review
from submissions.models import Submission
from .serializers import UserDetailSerializer, UserSerializer, PointsAdjustmentSerializer
from .models import User, PointsAdjustment
from .services import verify_firebase_token, get_firebase_user_info
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None):
        """Get user by ID"""
        try:
            user = get_object_or_404(User, pk=pk)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch user: {str(e)}'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's full profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """Update current user's profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        users = User.objects.order_by('-points')[:100]
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    try:
        id_token = request.data.get('idToken')
        if not id_token:
            return Response(
                {'error': 'No token provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add debug logging
        print(f"Attempting to verify token for Firebase...")
        
        # Verify the Firebase token and get decoded info
        try:
            decoded_token = verify_firebase_token(id_token)
            firebase_uid = decoded_token['uid']
            print(f"Successfully verified Firebase token for UID: {firebase_uid}")
        except Exception as e:
            print(f"Firebase verification failed: {str(e)}")
            return Response(
                {'error': f'Firebase verification failed: {str(e)}'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Try to get or create user
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            print(f"Found existing user with Firebase UID: {firebase_uid}")
        except User.DoesNotExist:
            print(f"Creating new user for Firebase UID: {firebase_uid}")
            # Get user info from Firebase
            firebase_user = get_firebase_user_info(firebase_uid)
            
            # Create new user with all required fields
            user = User.objects.create(
                email=firebase_user.email,
                name=firebase_user.display_name or firebase_user.email.split('@')[0],
                firebase_uid=firebase_uid,
                avatar=firebase_user.photo_url or '',
                provider=decoded_token.get('firebase', {})
                    .get('sign_in_provider', '')
                    .replace('.com', '')
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"Generated new JWT tokens for user: {user.email}")
        
        return Response({
            'token': access_token,
            'refresh': str(refresh),
            'user': UserDetailSerializer(user).data,
            'is_admin': user.is_staff or user.is_superuser  # Add this line
        })

    except Exception as e:
        print(f"Unexpected error in verify_token: {str(e)}")
        return Response(
            {'error': f'Authentication failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def platform_stats(self, request):
        """Get platform-wide statistics"""
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_points': User.objects.aggregate(total=models.Sum('points'))['total'],
            'average_points': User.objects.aggregate(avg=models.Avg('points'))['avg'],
            'submissions_count': Submission.objects.count(),
            'reviews_count': Review.objects.count(),
        }
        return Response(stats)

    @action(detail=True, methods=['post'])
    def adjust_points(self, request, pk=None):
        """Adjust user points"""
        user = self.get_object()
        points_delta = request.data.get('points_delta')
        reason = request.data.get('reason')
        
        if not points_delta:
            return Response(
                {'error': 'points_delta is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.adjust_points(points_delta, reason)
        return Response({'status': 'success', 'new_points': user.points})

    @action(detail=False, methods=['get'])
    def points_history(self, request):
        """Get points adjustment history"""
        adjustments = PointsAdjustment.objects.select_related('user', 'adjusted_by')
        serializer = PointsAdjustmentSerializer(adjustments, many=True)
        return Response(serializer.data)
