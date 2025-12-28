# teams/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Team, TeamMembership
from accounts.models import User


def is_admin(user):
    return user.is_authenticated and user.is_admin()


@login_required
def team_list(request):
    """List all teams"""
    if request.user.is_admin():
        teams = Team.objects.filter(is_active=True)
    else:
        # Team members can only see teams they belong to
        teams = Team.objects.filter(
            is_active=True,
            memberships__user=request.user,
            memberships__is_active=True
        ).distinct()
    
    context = {'teams': teams}
    return render(request, 'teams/team_list.html', context)


@user_passes_test(is_admin)
@login_required
def team_create(request):
    """Create new team (admin only)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if Team.objects.filter(name=name).exists():
            messages.error(request, 'Team name already exists')
            return render(request, 'teams/team_form.html')
        
        team = Team.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        messages.success(request, f'Team {name} created successfully!')
        return redirect('team_detail', team_id=team.id)
    
    return render(request, 'teams/team_form.html')


@login_required
def team_detail(request, team_id):
    """Team detail with members"""
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    # Check permissions
    if not request.user.is_admin() and not team.memberships.filter(user=request.user, is_active=True).exists():
        messages.error(request, 'Permission denied')
        return redirect('team_list')
    
    memberships = team.memberships.filter(is_active=True).order_by('role', 'joined_at')
    available_users = User.objects.filter(
        is_active=True,
        role='member'
    ).exclude(
        id__in=team.memberships.filter(is_active=True).values_list('user_id', flat=True)
    )
    
    context = {
        'team': team,
        'memberships': memberships,
        'available_users': available_users
    }
    return render(request, 'teams/team_detail.html', context)


@user_passes_test(is_admin)
@login_required
def team_edit(request, team_id):
    """Edit team (admin only)"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if Team.objects.filter(name=name).exclude(id=team_id).exists():
            messages.error(request, 'Team name already exists')
            return render(request, 'teams/team_form.html', {'team': team})
        
        team.name = name
        team.description = description
        team.save()
        
        messages.success(request, f'Team {name} updated successfully!')
        return redirect('team_detail', team_id=team.id)
    
    context = {'team': team, 'edit': True}
    return render(request, 'teams/team_form.html', context)


@user_passes_test(is_admin)
@login_required
def team_delete(request, team_id):
    """Delete team (admin only)"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        name = team.name
        team.is_active = False
        team.save()
        messages.success(request, f'Team {name} deleted successfully!')
        return redirect('team_list')
    
    context = {'team': team}
    return render(request, 'teams/team_confirm_delete.html', context)


@user_passes_test(is_admin)
@login_required
def add_team_member(request, team_id):
    """Add member to team (admin only)"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role = request.POST.get('role', 'member')
        
        user = get_object_or_404(User, id=user_id)
        
        # Check if user is already a member
        if team.memberships.filter(user=user, is_active=True).exists():
            messages.error(request, f'{user.get_full_name() or user.username} is already a member of this team')
        else:
            TeamMembership.objects.create(
                team=team,
                user=user,
                role=role
            )
            messages.success(request, f'{user.get_full_name() or user.username} added to team successfully!')
        
        return redirect('team_detail', team_id=team.id)
    
    return redirect('team_detail', team_id=team.id)


@user_passes_test(is_admin)
@login_required
def remove_team_member(request, team_id, membership_id):
    """Remove member from team (admin only)"""
    team = get_object_or_404(Team, id=team_id)
    membership = get_object_or_404(TeamMembership, id=membership_id, team=team)
    
    if request.method == 'POST':
        user_name = membership.user.get_full_name() or membership.user.username
        membership.is_active = False
        membership.save()
        messages.success(request, f'{user_name} removed from team successfully!')
        return redirect('team_detail', team_id=team.id)
    
    context = {'team': team, 'membership': membership}
    return render(request, 'teams/remove_member_confirm.html', context)
