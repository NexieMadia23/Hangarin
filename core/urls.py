from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main Dashboard
    path('', views.task_list, name='dashboard'),
    
    # Task CRUD
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    
    # Status Toggle (The 4-stage cycle: Starting -> In Progress -> Review -> Done)
    path('tasks/<int:pk>/toggle/', views.toggle_status, name='toggle_status'),
]