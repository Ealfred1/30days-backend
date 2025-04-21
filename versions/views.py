from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Version
from .serializers import VersionSerializer
from drf_spectacular.utils import extend_schema

# Create your views here.

@extend_schema(tags=['versions'])
class VersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('submissions')
