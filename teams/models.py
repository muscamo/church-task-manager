# teams/models.py
from django.db import models
from django.conf import settings
from accounts.models import User


class Team(models.Model):
    """Team model for organizing users"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'teams'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_member_count(self):
        return self.memberships.filter(is_active=True).count()

    def get_active_members(self):
        return User.objects.filter(
            team_memberships__team=self,
            team_memberships__is_active=True
        )


class TeamMembership(models.Model):
    """Through model for team memberships"""
    ROLE_CHOICES = [
        ('leader', 'Team Leader'),
        ('member', 'Team Member'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'team_memberships'
        unique_together = ['team', 'user']
        ordering = ['role', 'joined_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.team.name} ({self.get_role_display})"
