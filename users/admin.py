from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PointsAdjustment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'points', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'provider')
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'avatar')}),
        ('Firebase', {'fields': ('firebase_uid', 'provider')}),
        ('Points', {'fields': ('points',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    actions = ['add_points', 'deduct_points']
    
    def add_points(self, request, queryset):
        for user in queryset:
            user.adjust_points(100, "Admin bonus")
    add_points.short_description = "Add 100 points to selected users"
    
    def deduct_points(self, request, queryset):
        for user in queryset:
            user.adjust_points(-50, "Admin penalty")
    deduct_points.short_description = "Deduct 50 points from selected users"

@admin.register(PointsAdjustment)
class PointsAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'points_delta', 'reason', 'adjusted_by', 'created_at')
    list_filter = ('created_at', 'adjusted_by')
    search_fields = ('user__email', 'user__name', 'reason')