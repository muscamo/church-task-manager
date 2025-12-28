# tasks/templatetags/task_extras.py
"""
Custom template tags and filters for the tasks app
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a variable key.
    
    Usage in template:
        {{ my_dict|get_item:key_variable }}
    
    Example:
        {% for status_key, status_label in statuses %}
            {{ tasks_by_status|get_item:status_key }}
        {% endfor %}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def get_status_class(status):
    """
    Return CSS class for task status badge.
    
    Usage:
        <span class="{{ task.status|get_status_class }}">{{ task.get_status_display }}</span>
    """
    status_classes = {
        'todo': 'bg-gray-100 text-gray-800',
        'in_progress': 'bg-yellow-100 text-yellow-800',
        'waiting': 'bg-red-100 text-red-800',
        'completed': 'bg-green-100 text-green-800',
    }
    return status_classes.get(status, 'bg-gray-100 text-gray-800')


@register.filter
def get_priority_class(priority):
    """
    Return CSS class for priority badge.
    
    Usage:
        <span class="{{ task.priority|get_priority_class }}">{{ task.get_priority_display }}</span>
    """
    priority_classes = {
        'low': 'bg-green-100 text-green-800',
        'medium': 'bg-yellow-100 text-yellow-800',
        'high': 'bg-orange-100 text-orange-800',
        'urgent': 'bg-red-100 text-red-800',
    }
    return priority_classes.get(priority, 'bg-gray-100 text-gray-800')


@register.filter
def percentage(value, total):
    """
    Calculate percentage.
    
    Usage:
        {{ completed|percentage:total }}
    """
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0
