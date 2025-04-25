from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserDetailSerializer
from .models import User
from .services import verify_firebase_token, get_firebase_user_info
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

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
            return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the Firebase token
        decoded_token = verify_firebase_token(id_token)
        firebase_uid = decoded_token['uid']
        
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            # Get user info from Firebase 
            firebase_user = get_firebase_user_info(firebase_uid)
            
            # Create new user
            user = User.objects.create(
                email=firebase_user.email,
                name=firebase_user.display_name or '',
                firebase_uid=firebase_uid,
                avatar=firebase_user.photo_url or '',
                provider=decoded_token.get('firebase', {}).get('sign_in_provider', '').replace('google.com', 'google').replace('github.com', 'github')
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserDetailSerializer(user).data
        })

    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
