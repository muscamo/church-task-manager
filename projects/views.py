from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import OperationalError
from .models import Project, Board
from tasks.models import Task


@login_required
def project_list(request):
    """List all projects"""
    try:
        if request.user.is_admin():
            projects = Project.objects.filter(is_active=True)
        else:
            # Team members see projects they created or have tasks in
            projects = Project.objects.filter(
                is_active=True
            ).filter(
                Q(created_by=request.user) |
                Q(boards__tasks__assigned_to=request.user)
            ).distinct()
    except OperationalError as e:
        if "no such column" in str(e) or "no such table" in str(e):
            messages.error(request, 'Database schema not updated. Please run migrations first.')
            projects = Project.objects.none()
        else:
            raise e

    context = {'projects': projects}
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    """Project detail with boards"""
    project = get_object_or_404(Project, id=project_id)
    boards = project.boards.all()

    context = {
        'project': project,
        'boards': boards,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create(request):
    """Create new project (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Only admins can create projects')
        return redirect('project_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        team_id = request.POST.get('team')

        try:
            project = Project.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            
            # Only assign team if teams table exists and team_id is provided
            if team_id and team_id != '':
                try:
                    from teams.models import Team
                    team = Team.objects.get(id=team_id)
                    project.team = team
                    project.save()
                except (ImportError, Team.DoesNotExist, OperationalError):
                    # Teams table doesn't exist yet or team not found, skip team assignment
                    pass

            # Create default board
            Board.objects.create(
                project=project,
                name=f"{name} - Main Board",
                description="Primary task board"
            )

            messages.success(request, f'Project "{name}" created successfully!')
            return redirect('project_detail', project_id=project.id)
            
        except OperationalError as e:
            if "no such table" in str(e):
                messages.error(request, 'Database tables not created yet. Please run migrations first.')
            else:
                messages.error(request, f'Database error: {e}')
            return redirect('project_list')

    # Try to get teams for the form, but handle missing table gracefully
    teams = []
    try:
        from teams.models import Team
        teams = Team.objects.filter(is_active=True)
    except (ImportError, OperationalError):
        # Teams table doesn't exist yet
        pass

    return render(request, 'projects/project_form.html', {'teams': teams})


@login_required
def project_edit(request, project_id):
    """Edit project (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Only admins can edit projects')
        return redirect('project_list')

    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description', '')
        project.save()

        messages.success(request, 'Project updated successfully!')
        return redirect('project_detail', project_id=project.id)

    context = {'project': project, 'edit': True}
    return render(request, 'projects/project_form.html', context)


@login_required
def project_delete(request, project_id):
    """Delete project (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Only admins can delete projects')
        return redirect('project_list')

    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        project.is_active = False
        project.save()
        messages.success(
            request, f'Project "{project.name}" deleted successfully!')
        return redirect('project_list')

    context = {'project': project}
    return render(request, 'projects/project_confirm_delete.html', context)
