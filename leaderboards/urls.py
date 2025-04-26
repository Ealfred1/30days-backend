from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaderboardViewSet

router = DefaultRouter()
router.register('leaderboard', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('', include(router.urls)),
]    