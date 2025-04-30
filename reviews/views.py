from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, HelpfulMark
from .serializers import ReviewSerializer, HelpfulMarkSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# Create your views here.

@extend_schema(tags=['reviews'])
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get reviews with optional filtering"""
        return Review.objects.all().select_related('user')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new review"""
        try:
            # Extract only review-specific fields
            review_data = {
                'comment': request.data.get('comment'),
                'project': request.data.get('project'),
                'rating': request.data.get('rating'),
            }
            
            # Debug log
            print("Creating review with data:", review_data)
            
            serializer = ReviewSerializer(data=review_data)
            if serializer.is_valid():
                # Save the review with the current user
                review = serializer.save(user=request.user)
                
                # Debug log
                print("Review created successfully:", review)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            # Debug log
            print("Serializer errors:", serializer.errors)
            
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            # Debug log
            print("Error creating review:", str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        review = self.get_object()
        mark, created = HelpfulMark.objects.get_or_create(
            review=review,
            user=request.user
        )
        
        if created:
            review.helpful += 1
            review.save()
            return Response({'status': 'marked as helpful'})
        return Response({'status': 'already marked as helpful'})
