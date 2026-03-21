from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # --- Main Dashboard & Task CRUD ---
    path('', views.task_list, name='task_list'), 
    path('task/create/', views.task_create, name='task_create'),
    
    # This handles both the "Inline Quick Edit" (?inline=true) and the "Full Edit" modal
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/toggle/', views.toggle_status, name='toggle_status'),
    
    # --- Sidebar Detail View ---
    # Triggered when clicking the task name in the table
    path('task/<int:pk>/sidebar/', views.task_detail_sidebar, name='task_detail_sidebar'),

    # --- Subtask CRUD ---
    # Matches hx-post="{% url 'core:add_subtask' task.pk %}"
    path('task/<int:task_pk>/subtask/add/', views.add_subtask, name='add_subtask'),
    path('subtask/<int:sub_pk>/toggle/', views.toggle_subtask, name='toggle_subtask'),
    path('subtask/<int:sub_pk>/delete/', views.delete_subtask, name='delete_subtask'),

    # --- Notes CRUD ---
    # Matches hx-post="{% url 'core:add_note' task.pk %}" from your task_form.html
    path('task/<int:task_pk>/notes/add/', views.add_note, name='add_note'),
    
    # Keep this if you want to implement the "Autosave" or "Quick update" logic later
    path('task/<int:task_pk>/notes/update/', views.update_notes, name='update_notes'),
]