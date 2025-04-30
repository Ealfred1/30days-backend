from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, HelpfulMark
from .serializers import ReviewSerializer, HelpfulMarkSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

# Create your views here.

@extend_schema(tags=['reviews'])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a new review"""
        # Add the current user to the data
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """Get reviews with optional filtering"""
        queryset = Review.objects.all()
        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project=project)
        return queryset

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        review = self.get_object()
        mark, created = HelpfulMark.objects.get_or_create(
            review=review,
            user=request.user
        )
        
        if created:
            review.helpful_count += 1
            review.save()
            return Response({'status': 'marked as helpful'})
        return Response({'status': 'already marked as helpful'})
