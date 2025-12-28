from django.urls import path
from . import views, api

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('kanban/<int:board_id>/', views.kanban_view, name='kanban'),
    path('gantt/<int:project_id>/', views.gantt_view, name='gantt'),
    path('task/create/<int:board_id>/', views.task_create, name='task_create'),
    path('task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:task_id>/delete/', views.task_delete, name='task_delete'),

    # API endpoints
    path('api/task/status/', api.update_task_status, name='update_task_status'),
    path('api/task/<int:task_id>/progress/',
         api.update_task_progress, name='update_task_progress'),
]
