from django.urls import path
from . import views

app_name = 'core'

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/toggle/', views.toggle_status, name='toggle_status'),
    path('task/<int:pk>/sidebar/', views.task_detail_sidebar, name='task_detail_sidebar'),
    path('task/<int:task_pk>/subtask/add/', views.add_subtask, name='add_subtask'),
    path('subtask/<int:pk>/toggle/', views.toggle_subtask, name='toggle_subtask'),
    path('subtask/<int:pk>/delete/', views.delete_subtask, name='delete_subtask'),
    path('task/<int:task_pk>/notes/add/', views.add_note, name='add_note'),
    path('task/<int:task_pk>/notes/update/', views.update_notes, name='update_notes'),
    path('messages/', views.get_messages, name='get_messages'),
    path('notifications/', views.get_notifications, name='get_notifications'),
]