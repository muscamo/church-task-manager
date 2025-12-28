# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from tasks.models import Task
from .models import Notification


@receiver(post_save, sender=Task)
def task_assigned_notification(sender, instance, created, **kwargs):
    """Create notification when a task is assigned"""
    if created and instance.assigned_to and instance.assigned_to != instance.created_by:
        Notification.objects.create(
            user=instance.assigned_to,
            type='assigned',
            title=f"New Task Assigned: {instance.title}",
            message=f"You have been assigned a new task: {instance.title}",
            task=instance
        )


@receiver(post_save, sender=Task)
def task_completed_notification(sender, instance, **kwargs):
    """Create notification when a task is completed"""
    if instance.status == 'done':
        # Notify the task creator if different from who completed it
        if instance.created_by != instance.assigned_to:
            completed_by = instance.assigned_to.get_full_name() or instance.assigned_to.username if instance.assigned_to else "Someone"
            Notification.objects.create(
                user=instance.created_by,
                type='completed',
                title=f"Task Completed: {instance.title}",
                message=f"Task '{instance.title}' has been completed by {completed_by}.",
                task=instance
            )
