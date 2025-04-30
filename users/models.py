from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255)
    avatar = models.URLField(max_length=500, blank=True)
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    provider = models.CharField(max_length=50, blank=True)  # 'google' or 'github'
    bio = models.TextField(blank=True)
    github_username = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_submission_date = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            ("can_manage_points", "Can manage user points"),
            ("can_view_stats", "Can view platform statistics"),
            ("can_manage_versions", "Can manage challenge versions"),
        ]

    def __str__(self):
        return self.email

    def adjust_points(self, points_delta: int, reason: str = None):
        """Adjust user points with audit trail"""
        self.points += points_delta
        self.save()
        
        # Create points adjustment record
        PointsAdjustment.objects.create(
            user=self,
            points_delta=points_delta,
            reason=reason,
            adjusted_by=self.request.user if hasattr(self, 'request') else None
        )

class PointsAdjustment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_adjustments')
    points_delta = models.IntegerField()
    reason = models.TextField(null=True, blank=True)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='points_adjusted')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name}: {self.points_delta} points ({self.reason})"
