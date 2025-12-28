from django.contrib import admin
from .models import Project, Board


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by',
                    'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'description', 'created_by', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_at', 'task_count']
    list_filter = ['project', 'created_at']
    search_fields = ['name', 'description', 'project__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'
