from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from tasks.models import Task
from projects.models import Project
from django.contrib.auth import get_user_model
import csv
from datetime import datetime

User = get_user_model()


@login_required
def report_view(request):
    """Reporting view with filters"""
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project')
    user_id = request.GET.get('user')
    status = request.GET.get('status')

    # Base queryset
    if request.user.is_admin():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    # Apply filters
    if start_date:
        tasks = tasks.filter(created_at__gte=start_date)
    if end_date:
        tasks = tasks.filter(created_at__lte=end_date)
    if project_id:
        tasks = tasks.filter(board__project_id=project_id)
    if user_id:
        tasks = tasks.filter(assigned_to_id=user_id)
    if status:
        tasks = tasks.filter(status=status)

    # Generate reports
    tasks_completed_per_user = {}
    if request.user.is_admin():
        for user in User.objects.filter(is_active=True):
            user_tasks = tasks.filter(assigned_to=user, status='completed')
            tasks_completed_per_user[user.get_full_name(
            ) or user.username] = user_tasks.count()

    overdue_tasks = tasks.filter(
        due_date__lt=datetime.now().date(),
        status__in=['todo', 'in_progress', 'waiting']
    )

    # Project completion
    projects = Project.objects.filter(is_active=True)
    project_completion = []
    for project in projects:
        project_tasks = tasks.filter(board__project=project)
        total = project_tasks.count()
        completed = project_tasks.filter(status='completed').count()
        percentage = (completed / total * 100) if total > 0 else 0
        project_completion.append({
            'project': project.name,
            'total': total,
            'completed': completed,
            'percentage': round(percentage, 1)
        })

    # Get all projects and users for filters
    all_projects = Project.objects.filter(is_active=True)
    all_users = User.objects.filter(is_active=True)

    context = {
        'tasks_completed_per_user': tasks_completed_per_user,
        'overdue_tasks': overdue_tasks,
        'project_completion': project_completion,
        'all_projects': all_projects,
        'all_users': all_users,
        'task_statuses': Task.STATUS_CHOICES,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'project_id': project_id,
            'user_id': user_id,
            'status': status,
        }
    }

    return render(request, 'reports/report_view.html', context)


@login_required
def export_report_csv(request):
    """Export report to CSV"""
    # Get same filters as report_view
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project')
    user_id = request.GET.get('user')
    status = request.GET.get('status')

    if request.user.is_admin():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    # Apply filters
    if start_date:
        tasks = tasks.filter(created_at__gte=start_date)
    if end_date:
        tasks = tasks.filter(created_at__lte=end_date)
    if project_id:
        tasks = tasks.filter(board__project_id=project_id)
    if user_id:
        tasks = tasks.filter(assigned_to_id=user_id)
    if status:
        tasks = tasks.filter(status=status)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Project', 'Board', 'Assigned To', 'Status',
                    'Priority', 'Progress', 'Due Date', 'Created At', 'Created By'])

    for task in tasks.select_related('board__project', 'assigned_to', 'created_by'):
        writer.writerow([
            task.title,
            task.board.project.name,
            task.board.name,
            task.assigned_to.get_full_name() if task.assigned_to else 'Unassigned',
            task.get_status_display(),
            task.get_priority_display(),
            f"{task.progress}%",
            task.due_date or 'N/A',
            task.created_at.strftime('%Y-%m-%d %H:%M'),
            task.created_by.get_full_name(),
        ])

    return response


@login_required
def export_report_pdf(request):
    """Export report to PDF"""
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO

    # Get same filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project')
    user_id = request.GET.get('user')
    status = request.GET.get('status')

    if request.user.is_admin():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    # Apply filters
    if start_date:
        tasks = tasks.filter(created_at__gte=start_date)
    if end_date:
        tasks = tasks.filter(created_at__lte=end_date)
    if project_id:
        tasks = tasks.filter(board__project_id=project_id)
    if user_id:
        tasks = tasks.filter(assigned_to_id=user_id)
    if status:
        tasks = tasks.filter(status=status)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Church Task Management Report", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))

    # Create table data
    data = [['Title', 'Project', 'Assigned To',
             'Status', 'Priority', 'Progress', 'Due Date']]

    # Limit to 50 for PDF
    for task in tasks.select_related('board__project', 'assigned_to')[:50]:
        data.append([
            task.title[:30],
            task.board.project.name[:20],
            (task.assigned_to.get_full_name()[
             :20] if task.assigned_to else 'Unassigned'),
            task.get_status_display(),
            task.get_priority_display(),
            f"{task.progress}%",
            str(task.due_date) if task.due_date else 'N/A',
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tasks_report.pdf"'

    return response
