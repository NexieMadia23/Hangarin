from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Verify the name is 'task_list'
    path('', views.task_list, name='task_list'), 
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/toggle/', views.toggle_status, name='toggle_status'),
    path('task/<int:task_pk>/subtask/add/', views.add_subtask, name='add_subtask'),
    path('task/<int:task_pk>/note/add/', views.add_note, name='add_note'),
]