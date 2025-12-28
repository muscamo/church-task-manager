# notifications/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """View to list all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark notifications as read when viewed
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
        'unread_count': Notification.get_unread_count(request.user),
        'overdue_count': Notification.get_overdue_count(request.user),
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def get_notification_counts(request):
    """Get notification counts for the current user"""
    return JsonResponse({
        'unread_count': Notification.get_unread_count(request.user),
        'overdue_count': Notification.get_overdue_count(request.user),
    })
