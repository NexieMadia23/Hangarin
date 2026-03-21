from django.contrib import admin
from .models import Category, Priority, Task, SubTask, Note

# --- Inlines for a better Workflow ---

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1  # Shows one empty row by default
    # Requirement: Use 'status' (Pending, In Progress, Completed) instead of a checkbox
    fields = ('title', 'status') 

class NoteInline(admin.StackedInline):
    model = Note
    extra = 0  

# --- Model Admins ---

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # Requirement: Display title, status, deadline, priority, category
    list_display = ('title', 'status', 'deadline', 'priority', 'category')
    # Requirement: Add filters for status, priority, category
    list_filter = ('status', 'priority', 'category')
    # Requirement: Enable search on title and description
    search_fields = ('title', 'description')
    inlines = [SubTaskInline, NoteInline]
    
    fieldsets = (
        ('Main Info', {
            'fields': ('title', 'description', 'status')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'deadline')
        }),
    )

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    # Requirement: Display title, status, and custom field parent_task_name
    list_display = ('title', 'status', 'parent_task_name')
    # Requirement: Filter by status
    list_filter = ('status',)
    # Requirement: Enable search on title
    search_fields = ('title',)

    # Custom field requirement
    def parent_task_name(self, obj):
        return obj.task.title
    parent_task_name.short_description = 'Parent Task Name'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Requirement: Display name and make searchable
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    # Requirement: Display name and make searchable
    list_display = ('name', 'level', 'color')
    list_editable = ('level', 'color')
    search_fields = ('name',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    # Requirement: Display task, content, and created_at
    list_display = ('task', 'content_snippet', 'created_at')
    # Requirement: Filter by created_at
    list_filter = ('created_at',)
    # Requirement: Enable search on content
    search_fields = ('content',)

    def content_snippet(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'