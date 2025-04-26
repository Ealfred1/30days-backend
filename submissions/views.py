from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Submission, Technology
from .serializers import SubmissionSerializer, TechnologySerializer, SubmissionDetailSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.

@extend_schema(tags=['submissions'])
class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = Submission.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return SubmissionDetailSerializer
        return SubmissionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='version', description='Filter by version ID', required=False, type=int),
        ]
    )
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        submissions = self.get_queryset().order_by('-created_at')
        serializer = SubmissionDetailSerializer(submissions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SubmissionDetailSerializer(instance)
        return Response(serializer.data)

@extend_schema(tags=['technologies'])
class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
