from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubmissionViewSet, TechnologyViewSet

router = DefaultRouter()
router.register(r'submissions', SubmissionViewSet)
router.register(r'technologies', TechnologyViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 