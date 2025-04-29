from django.urls import path
from .views import VersionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'versions', VersionViewSet, basename='version')

urlpatterns = router.urls 