from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, HelpfulMark
from .serializers import ReviewSerializer, HelpfulMarkSerializer
from drf_spectacular.utils import extend_schema

# Create your views here.

@extend_schema(tags=['reviews'])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['submission', 'reviewer']

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

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
