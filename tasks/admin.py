from django.contrib import admin
from .models import Task, TaskDependency


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'assigned_to', 'status',
                    'priority', 'progress', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority',
                   'board__project', 'assigned_to', 'created_at']
    search_fields = ['title', 'description',
                     'board__name', 'board__project__name']
    date_hierarchy = 'due_date'
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Task Information', {
            'fields': ('board', 'title', 'description')
        }),
        ('Assignment & Status', {
            'fields': ('assigned_to', 'status', 'priority', 'progress')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'order'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['task', 'depends_on']
    search_fields = ['task__title', 'depends_on__title']
    autocomplete_fields = ['task', 'depends_on']
