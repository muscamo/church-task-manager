# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Team Member'),
    ]

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='member')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        db_table = 'users'

    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
