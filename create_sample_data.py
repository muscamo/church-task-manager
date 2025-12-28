#!/usr/bin/env python
"""
Sample Data Generator for Task Steward
Run this script to populate the database with sample data for testing
"""

from django.utils import timezone
from datetime import timedelta
import django
import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django environment BEFORE importing ANY models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_task_manager.settings')

django.setup()

# NOW import Django models AFTER django.setup()


def create_sample_data():
    # Import models inside the function after Django is set up
    from accounts.models import User
    from projects.models import Project, Board
    from tasks.models import Task

    print("=" * 60)
    print("Creating sample data for Task Steward")
    print("=" * 60)

    # Clear existing data (optional - comment out if you want to keep existing data)
    print("\n[1/5] Clearing existing data...")
    Task.objects.all().delete()
    Board.objects.all().delete()
    Project.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print("✓ Existing data cleared")

    # Create Admin User
    print("\n[2/5] Creating users...")
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@church.org',
            'first_name': 'John',
            'last_name': 'Pastor',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"✓ Admin user created: admin / admin123")
    else:
        print(f"✓ Admin user already exists: admin")

    # Create Team Members
    members_data = [
        ('member1', 'Sarah', 'Worship', 'sarah@church.org'),
        ('member2', 'Michael', 'Youth', 'michael@church.org'),
        ('member3', 'Emma', 'Children', 'emma@church.org'),
        ('member4', 'David', 'Outreach', 'david@church.org'),
    ]

    members = []
    for username, first_name, last_name, email in members_data:
        member, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'member',
            }
        )
        if created:
            member.set_password('member123')
            member.save()
            print(f"✓ Team member created: {username} / member123")
        else:
            print(f"✓ Team member already exists: {username}")
        members.append(member)

    # Create Projects and Boards
    print("\n[3/5] Creating projects and boards...")

    projects_data = [
        {
            'name': 'Sunday Service Planning',
            'description': 'Weekly service coordination and preparation tasks',
            'boards': ['Main Service Board', 'Special Events']
        },
        {
            'name': 'Youth Ministry',
            'description': 'Youth group activities, events, and outreach programs',
            'boards': ['Youth Events', 'Youth Projects']
        },
        {
            'name': 'Community Outreach',
            'description': 'Community service initiatives and partnership programs',
            'boards': ['Outreach Activities', 'Community Partnerships']
        },
    ]

    all_boards = []
    for proj_data in projects_data:
        project = Project.objects.create(
            name=proj_data['name'],
            description=proj_data['description'],
            created_by=admin
        )
        print(f"✓ Project created: {project.name}")

        for board_name in proj_data['boards']:
            board = Board.objects.create(
                project=project,
                name=board_name,
                description=f"Task board for {board_name}"
            )
            all_boards.append(board)
            print(f"  └─ Board created: {board_name}")

    # Create Tasks
    print("\n[4/5] Creating tasks...")

    tasks_data = [
        # Sunday Service Planning Tasks
        {
            'board_index': 0,  # Main Service Board
            'title': 'Prepare worship song list',
            'description': 'Select and coordinate 5-6 worship songs for Sunday service including opening, worship set, and closing song',
            'status': 'completed',
            'priority': 'high',
            'progress': 100,
            'assigned_to': members[0],  # Sarah
            'due_date': timezone.now().date() - timedelta(days=2),
            'start_date': timezone.now().date() - timedelta(days=9)
        },
        {
            'board_index': 0,
            'title': 'Review and finalize sermon notes',
            'description': 'Complete sermon outline and coordinate with media team for presentation slides',
            'status': 'in_progress',
            'priority': 'urgent',
            'progress': 75,
            'assigned_to': admin,
            'due_date': timezone.now().date() + timedelta(days=1),
            'start_date': timezone.now().date() - timedelta(days=7)
        },
        {
            'board_index': 0,
            'title': 'Test audio/visual equipment',
            'description': 'Complete sound check, test microphones, projector, and livestream setup',
            'status': 'todo',
            'priority': 'high',
            'progress': 0,
            'assigned_to': members[1],  # Michael
            'due_date': timezone.now().date() + timedelta(days=2),
            'start_date': timezone.now().date()
        },
        {
            'board_index': 0,
            'title': 'Coordinate volunteer schedule',
            'description': 'Confirm greeters, ushers, and parking team for Sunday service',
            'status': 'in_progress',
            'priority': 'medium',
            'progress': 50,
            'assigned_to': members[2],  # Emma
            'due_date': timezone.now().date() + timedelta(days=3),
            'start_date': timezone.now().date() - timedelta(days=3)
        },
        {
            'board_index': 0,
            'title': 'Prepare communion elements',
            'description': 'Purchase bread and juice, prepare communion trays for distribution',
            'status': 'waiting',
            'priority': 'medium',
            'progress': 25,
            'assigned_to': members[3],  # David
            'due_date': timezone.now().date() + timedelta(days=4),
            'start_date': timezone.now().date() - timedelta(days=2)
        },

        # Youth Ministry Tasks
        {
            'board_index': 2,  # Youth Events
            'title': 'Plan summer youth camp',
            'description': 'Coordinate dates, venue, activities, and registration for annual summer youth camp',
            'status': 'in_progress',
            'priority': 'high',
            'progress': 40,
            'assigned_to': members[1],  # Michael
            'due_date': timezone.now().date() + timedelta(days=30),
            'start_date': timezone.now().date() - timedelta(days=10)
        },
        {
            'board_index': 2,
            'title': 'Organize Friday game night',
            'description': 'Setup games, snacks, and activities for youth fellowship night',
            'status': 'todo',
            'priority': 'medium',
            'progress': 0,
            'assigned_to': members[1],
            'due_date': timezone.now().date() + timedelta(days=5),
            'start_date': timezone.now().date() + timedelta(days=2)
        },
        {
            'board_index': 2,
            'title': 'Update youth group social media',
            'description': 'Post weekly updates, photos, and upcoming events on Instagram and Facebook',
            'status': 'in_progress',
            'priority': 'low',
            'progress': 60,
            'assigned_to': members[1],
            'due_date': timezone.now().date() + timedelta(days=7),
            'start_date': timezone.now().date() - timedelta(days=5)
        },

        # Community Outreach Tasks
        {
            'board_index': 4,  # Outreach Activities
            'title': 'Food pantry distribution',
            'description': 'Organize volunteers and distribute food packages to families in need',
            'status': 'completed',
            'priority': 'high',
            'progress': 100,
            'assigned_to': members[3],  # David
            'due_date': timezone.now().date() - timedelta(days=1),
            'start_date': timezone.now().date() - timedelta(days=8)
        },
        {
            'board_index': 4,
            'title': 'Partner with local school',
            'description': 'Meet with principal to discuss tutoring program and school supply drive',
            'status': 'in_progress',
            'priority': 'medium',
            'progress': 30,
            'assigned_to': members[3],
            'due_date': timezone.now().date() + timedelta(days=14),
            'start_date': timezone.now().date() - timedelta(days=7)
        },
        {
            'board_index': 4,
            'title': 'Plan community cleanup day',
            'description': 'Organize neighborhood cleanup event with volunteers and supplies',
            'status': 'todo',
            'priority': 'medium',
            'progress': 0,
            'assigned_to': members[3],
            'due_date': timezone.now().date() + timedelta(days=21),
            'start_date': timezone.now().date() + timedelta(days=5)
        },

        # Special Events
        {
            'board_index': 1,  # Special Events
            'title': 'Easter Sunday service preparation',
            'description': 'Plan special Easter service including music, decorations, and outreach',
            'status': 'todo',
            'priority': 'urgent',
            'progress': 0,
            'assigned_to': admin,
            'due_date': timezone.now().date() + timedelta(days=60),
            'start_date': timezone.now().date() + timedelta(days=15)
        },
        {
            'board_index': 1,
            'title': 'Church anniversary celebration',
            'description': 'Coordinate 50th anniversary event including program, catering, and invitations',
            'status': 'in_progress',
            'priority': 'high',
            'progress': 20,
            'assigned_to': members[0],
            'due_date': timezone.now().date() + timedelta(days=45),
            'start_date': timezone.now().date() - timedelta(days=5)
        },

        # Overdue task for testing
        {
            'board_index': 0,
            'title': 'Update church website content',
            'description': 'Refresh homepage content and add new ministry photos',
            'status': 'todo',
            'priority': 'medium',
            'progress': 0,
            'assigned_to': members[2],
            'due_date': timezone.now().date() - timedelta(days=5),
            'start_date': timezone.now().date() - timedelta(days=15)
        },
    ]

    created_tasks = []
    for task_data in tasks_data:
        board = all_boards[task_data.pop('board_index')]
        task = Task.objects.create(
            board=board,
            created_by=admin,
            **task_data
        )
        created_tasks.append(task)
        status_emoji = '✓' if task.status == 'completed' else '→' if task.status == 'in_progress' else '⏸' if task.status == 'waiting' else '○'
        print(
            f"{status_emoji} Task created: {task.title} ({task.get_status_display()})")

    print(f"\n✓ Total tasks created: {len(created_tasks)}")

    # Summary
    print("\n[5/5] Summary")
    print("=" * 60)
    print(f"✓ Users created: {User.objects.count()}")
    print(f"  - Admin users: {User.objects.filter(role='admin').count()}")
    print(f"  - Team members: {User.objects.filter(role='member').count()}")
    print(f"✓ Projects created: {Project.objects.count()}")
    print(f"✓ Boards created: {Board.objects.count()}")
    print(f"✓ Tasks created: {Task.objects.count()}")
    print(f"  - Completed: {Task.objects.filter(status='completed').count()}")
    print(
        f"  - In Progress: {Task.objects.filter(status='in_progress').count()}")
    print(f"  - Waiting: {Task.objects.filter(status='waiting').count()}")
    print(f"  - To Do: {Task.objects.filter(status='todo').count()}")
    print(
        f"  - Overdue: {len([t for t in Task.objects.all() if t.is_overdue()])}")

    print("\n" + "=" * 60)
    print("Sample data created successfully! 🎉")
    print("=" * 60)
    print("\nLogin Credentials:")
    print("-" * 60)
    print("Admin Account:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nTeam Member Accounts:")
    print("  Username: member1, member2, member3, member4")
    print("  Password: member123")
    print("-" * 60)
    print("\nYou can now run: python manage.py runserver")
    print("Then visit: http://127.0.0.1:8000")
    print("=" * 60)


if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
