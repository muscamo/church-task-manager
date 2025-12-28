from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import User


def is_admin(user):
    return user.is_authenticated and user.is_admin()


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {'user': request.user}
    return render(request, 'accounts/profile.html', context)


@user_passes_test(is_admin)
@login_required
def user_list(request):
    """List all users for admin management"""
    users = User.objects.all().order_by('username')
    context = {'users': users}
    return render(request, 'accounts/user_list.html', context)


@user_passes_test(is_admin)
@login_required
def user_create(request):
    """Create new user (admin only)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'member')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/user_form.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone
        )
        messages.success(request, f'User {username} created successfully!')
        return redirect('user_list')
    
    return render(request, 'accounts/user_form.html')


@user_passes_test(is_admin)
@login_required
def user_edit(request, user_id):
    """Edit user (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.role = request.POST.get('role')
        user.phone = request.POST.get('phone', '')
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('user_list')
    
    context = {'user': user, 'edit': True}
    return render(request, 'accounts/user_form.html', context)


@user_passes_test(is_admin)
@login_required
def user_delete(request, user_id):
    """Delete user (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'You cannot delete your own account')
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('user_list')
    
    context = {'user': user}
    return render(request, 'accounts/user_confirm_delete.html', context)
