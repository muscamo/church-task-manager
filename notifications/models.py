# notifications/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from tasks.models import Task


class Notification(models.Model):
    """Notification model for user alerts"""
    TYPE_CHOICES = [
        ('overdue', 'Overdue Task'),
        ('due_soon', 'Task Due Soon'),
        ('assigned', 'Task Assigned'),
        ('completed', 'Task Completed'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @classmethod
    def create_overdue_notifications(cls):
        """Create notifications for overdue tasks"""
        from django.db.models import Q
        
        # Find overdue tasks
        overdue_tasks = Task.objects.filter(
            Q(due_date__lt=timezone.now().date()) | 
            (Q(due_date=timezone.now().date()) & Q(due_date__isnull=False)),
            status__in=['todo', 'in_progress']
        )
        
        notifications = []
        for task in overdue_tasks:
            # Check if we already have an unread overdue notification for this task
            existing = cls.objects.filter(task=task, type='overdue', is_read=False).exists()
            
            if not existing:
                # Create notification for assigned user
                if task.assigned_to:
                    notifications.append(cls(
                        user=task.assigned_to,
                        type='overdue',
                        title=f"Overdue Task: {task.title}",
                        message=f"Task '{task.title}' was due on {task.due_date} and is now overdue.",
                        task=task
                    ))
                
                # Create notification for task creator if different from assigned user
                if task.created_by != task.assigned_to:
                    notifications.append(cls(
                        user=task.created_by,
                        type='overdue',
                        title=f"Overdue Task: {task.title}",
                        message=f"Task '{task.title}' assigned to {task.assigned_to.get_full_name() or task.assigned_to.username} is overdue.",
                        task=task
                    ))
        
        if notifications:
            cls.objects.bulk_create(notifications)
            return len(notifications)
        return 0
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def get_overdue_count(cls, user):
        """Get count of overdue task notifications for a user"""
        return cls.objects.filter(user=user, type='overdue', is_read=False).count()
