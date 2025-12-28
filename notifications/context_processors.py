# notifications/context_processors.py
from .models import Notification


def notification_counts(request):
    """Add notification counts to all templates"""
    if request.user.is_authenticated:
        return {
            'unread_count': Notification.get_unread_count(request.user),
            'overdue_count': Notification.get_overdue_count(request.user),
        }
    return {
        'unread_count': 0,
        'overdue_count': 0,
    }
