from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, verify_token, logout

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/verify-token/', verify_token, name='verify_token'),
    path('auth/logout/', logout, name='logout'),
] 