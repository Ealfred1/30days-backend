from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Submission, Technology
from .serializers import SubmissionSerializer, TechnologySerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

@extend_schema(tags=['submissions'])
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['version', 'user', 'day_number']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'day_number']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='version', description='Filter by version ID', required=False, type=int),
        ]
    )
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        submissions = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)

@extend_schema(tags=['technologies'])
class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
