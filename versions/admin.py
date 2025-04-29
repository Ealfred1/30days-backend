from django.contrib import admin
from .models import Version

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'codename', 'start_date', 'end_date', 
                   'is_active', 'status', 'participant_count', 'submission_count')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'codename', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-number',)

    fieldsets = (
        (None, {
            'fields': ('name', 'number', 'codename', 'description')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Additional Info', {
            'fields': ('focus_area', 'technologies')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
