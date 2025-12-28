from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Task
import json


@login_required
@require_http_methods(["POST"])
def update_task_status(request):
    """API endpoint to update task status via HTMX"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')

        task = Task.objects.get(id=task_id)

        # Check permissions
        if not request.user.is_admin() and task.assigned_to != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        task.status = new_status
        if new_status == 'completed':
            task.progress = 100
        task.save()

        return JsonResponse({'success': True, 'status': new_status})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_task_progress(request, task_id):
    """API endpoint to update task progress"""
    try:
        task = Task.objects.get(id=task_id)

        # Check permissions
        if not request.user.is_admin() and task.assigned_to != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        data = json.loads(request.body)
        progress = int(data.get('progress', 0))

        if 0 <= progress <= 100:
            task.progress = progress
            if progress == 100:
                task.status = 'completed'
            task.save()
            return JsonResponse({'success': True, 'progress': progress})
        else:
            return JsonResponse({'error': 'Progress must be between 0 and 100'}, status=400)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
