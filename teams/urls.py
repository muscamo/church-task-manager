# teams/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.team_create, name='team_create'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('<int:team_id>/delete/', views.team_delete, name='team_delete'),
    path('<int:team_id>/add-member/', views.add_team_member, name='add_team_member'),
    path('<int:team_id>/remove-member/<int:membership_id>/', views.remove_team_member, name='remove_team_member'),
]
