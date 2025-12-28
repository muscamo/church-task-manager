# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import Task, Board
from projects.models import Project
from notifications.models import Notification


@login_required
def kanban_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if not request.user.is_admin() and board.project.created_by != request.user:
        tasks = board.tasks.filter(assigned_to=request.user)
    else:
        tasks = board.tasks.all()

    tasks_by_status = {
        'todo': tasks.filter(status='todo'),
        'in_progress': tasks.filter(status='in_progress'),
        'waiting': tasks.filter(status='waiting'),
        'completed': tasks.filter(status='completed'),
    }

    context = {
        'board': board,
        'tasks_by_status': tasks_by_status,
        'statuses': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/kanban.html', context)


@login_required
def dashboard_view(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.user.is_admin():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now().date(),
        status__in=['todo', 'in_progress', 'waiting']
    )

    tasks_by_status = {
        'todo': tasks.filter(status='todo').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'waiting': tasks.filter(status='waiting').count(),
        'completed': completed_tasks,
    }

    if request.user.is_admin():
        users = User.objects.filter(is_active=True)
        tasks_per_user = []
        for user in users:
            user_tasks = Task.objects.filter(assigned_to=user)
            tasks_per_user.append({
                'user': user.get_full_name() or user.username,
                'total': user_tasks.count(),
                'completed': user_tasks.filter(status='completed').count(),
            })
    else:
        tasks_per_user = []

    completion_percentage = (
        completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    recent_tasks = tasks.order_by('-created_at')[:10]

    context = {
        'total_tasks': total_tasks,
        'tasks_by_status': tasks_by_status,
        'overdue_tasks': overdue_tasks,
        'tasks_per_user': tasks_per_user,
        'completion_percentage': round(completion_percentage, 1),
        'recent_tasks': recent_tasks,
        'unread_count': Notification.get_unread_count(request.user),
        'overdue_count': Notification.get_overdue_count(request.user),
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def gantt_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    tasks = Task.objects.filter(
        board__project=project,
        start_date__isnull=False,
        due_date__isnull=False
    ).select_related('assigned_to', 'board')

    can_edit = request.user.is_admin() or project.created_by == request.user

    context = {
        'project': project,
        'tasks': tasks,
        'can_edit': can_edit,
    }
    return render(request, 'tasks/gantt.html', context)


@login_required
def task_create(request, board_id):
    """Create new task"""
    from projects.models import Board
    from django.contrib.auth import get_user_model
    User = get_user_model()

    board = get_object_or_404(Board, id=board_id)

    # Check permissions - admins, project creators, and team members can create tasks
    if not request.user.is_admin() and board.project.created_by != request.user and request.user not in board.project.members.all():
        messages.error(request, 'Permission denied')
        return redirect('kanban', board_id=board_id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        due_date = request.POST.get('due_date')
        
        # Validate that start date is before due date
        if start_date and due_date:
            from datetime import datetime
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                due_dt = datetime.strptime(due_date, '%Y-%m-%d').date()
                
                if start_dt > due_dt:
                    messages.error(request, 'Start date must be before due date')
                    users = User.objects.filter(is_active=True)
                    context = {
                        'board': board,
                        'users': users,
                        'priorities': Task.PRIORITY_CHOICES,
                        'statuses': Task.STATUS_CHOICES,
                    }
                    return render(request, 'tasks/task_form.html', context)
            except ValueError:
                messages.error(request, 'Invalid date format')
                users = User.objects.filter(is_active=True)
                context = {
                    'board': board,
                    'users': users,
                    'priorities': Task.PRIORITY_CHOICES,
                    'statuses': Task.STATUS_CHOICES,
                }
                return render(request, 'tasks/task_form.html', context)
        
        task = Task.objects.create(
            board=board,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            notes=request.POST.get('notes', ''),
            status=request.POST.get('status', 'todo'),
            priority=request.POST.get('priority', 'medium'),
            assigned_to_id=request.POST.get('assigned_to') or None,
            due_date=due_date or None,
            start_date=start_date or None,
            created_by=request.user
        )

        messages.success(request, 'Task created successfully!')
        return redirect('kanban', board_id=board_id)

    users = User.objects.filter(is_active=True)
    
    # Check if the project has a team relationship (projects may not have teams)
    team_members = []
    if hasattr(board.project, 'team') and board.project.team:
        team_members = board.project.team.get_active_members()
        # Combine all users with team members, remove duplicates
        users = (users | team_members).distinct()
    
    context = {
        'board': board,
        'users': users,
        'priorities': Task.PRIORITY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_edit(request, task_id):
    """Edit task"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    task = get_object_or_404(Task, id=task_id)

    # Check permissions - admins, assigned users, and task creators can edit tasks
    if not request.user.is_admin() and task.assigned_to != request.user and task.created_by != request.user:
        messages.error(request, 'Permission denied')
        return redirect('kanban', board_id=task.board.id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        due_date = request.POST.get('due_date')
        
        # Validate that start date is before due date
        if start_date and due_date:
            from datetime import datetime
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                due_dt = datetime.strptime(due_date, '%Y-%m-%d').date()
                
                if start_dt > due_dt:
                    messages.error(request, 'Start date must be before due date')
                    users = User.objects.filter(is_active=True)
                    context = {
                        'task': task,
                        'users': users,
                        'priorities': Task.PRIORITY_CHOICES,
                        'statuses': Task.STATUS_CHOICES,
                        'edit': True,
                    }
                    return render(request, 'tasks/task_form.html', context)
            except ValueError:
                messages.error(request, 'Invalid date format')
                users = User.objects.filter(is_active=True)
                context = {
                    'task': task,
                    'users': users,
                    'priorities': Task.PRIORITY_CHOICES,
                    'statuses': Task.STATUS_CHOICES,
                    'edit': True,
                }
                return render(request, 'tasks/task_form.html', context)
        
        task.title = request.POST.get('title')
        task.description = request.POST.get('description', '')
        task.notes = request.POST.get('notes', '')
        task.status = request.POST.get('status')
        task.priority = request.POST.get('priority')
        task.assigned_to_id = request.POST.get('assigned_to') or None
        task.due_date = due_date or None
        task.start_date = start_date or None
        task.progress = int(request.POST.get('progress', 0))
        task.save()

        messages.success(request, 'Task updated successfully!')
        return redirect('kanban', board_id=task.board.id)

    users = User.objects.filter(is_active=True)
    
    # Check if the project has a team relationship (projects may not have teams)
    team_members = []
    if hasattr(task.board.project, 'team') and task.board.project.team:
        team_members = task.board.project.team.get_active_members()
        # Combine all users with team members, remove duplicates
        users = (users | team_members).distinct()
    
    context = {
        'task': task,
        'users': users,
        'priorities': Task.PRIORITY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
        'edit': True,
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_delete(request, task_id):
    """Delete task"""
    task = get_object_or_404(Task, id=task_id)
    board_id = task.board.id

    # Check permissions
    if not request.user.is_admin() and task.created_by != request.user:
        messages.error(request, 'Permission denied')
        return redirect('kanban', board_id=board_id)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('kanban', board_id=board_id)

    context = {'task': task}
    return render(request, 'tasks/task_confirm_delete.html', context)
