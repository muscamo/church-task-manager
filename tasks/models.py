# tasks/models.py
from django.db import models
from django.conf import settings
from projects.models import Board


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting/Blocked'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Progress notes and updates")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'tasks'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            from django.utils import timezone
            return self.due_date < timezone.now().date()
        return False


class TaskDependency(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='dependent_tasks')

    class Meta:
        db_table = 'task_dependencies'
        unique_together = ['task', 'depends_on']

    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on.title}"
