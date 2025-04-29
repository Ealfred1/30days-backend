from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Version
from .serializers import VersionSerializer, VersionComparisonSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

@extend_schema(tags=['versions'])
class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            today = timezone.now().date()
            if status_filter == 'active':
                queryset = queryset.filter(start_date__lte=today, end_date__gte=today)
            elif status_filter == 'completed':
                queryset = queryset.filter(end_date__lt=today)
            elif status_filter == 'upcoming':
                queryset = queryset.filter(start_date__gt=today)

        return queryset.prefetch_related('submissions')

    @action(detail=False, methods=['get'])
    def current(self):
        """Get the currently active version"""
        version = Version.objects.filter(is_active=True).first()
        if not version:
            return Response({'error': 'No active version found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(version)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a specific version and deactivate others"""
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        Version.objects.all().update(is_active=False)
        version = self.get_object()
        version.is_active = True
        version.save()
        return Response({'status': 'version activated'})

    @action(detail=False, methods=['get'])
    def compare(self, request):
        """Compare two versions"""
        version1_id = request.query_params.get('version1')
        version2_id = request.query_params.get('version2')
        
        try:
            v1 = Version.objects.get(id=version1_id)
            v2 = Version.objects.get(id=version2_id)
            
            comparison = {
                'version1': v1,
                'version2': v2,
                'participant_difference': v1.participant_count - v2.participant_count,
                'submission_difference': v1.submission_count - v2.submission_count,
                'technology_overlap': list(set(v1.technologies) & set(v2.technologies))
            }
            
            serializer = VersionComparisonSerializer(comparison)
            return Response(serializer.data)
            
        except Version.DoesNotExist:
            return Response(
                {'error': 'One or both versions not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed statistics for a version"""
        version = self.get_object()
        stats = {
            'daily_submissions': {}, # You'll need to implement this
            'top_technologies': {}, # You'll need to implement this
            'completion_rate': 0, # You'll need to implement this
            'average_score': 0, # You'll need to implement this
        }
        return Response(stats)
