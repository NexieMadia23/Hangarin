from django.contrib import admin
from .models import Category, Priority, Task, SubTask, Note

# --- Inlines for a better Workflow ---

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1  # Shows one empty row by default

class NoteInline(admin.StackedInline):
    model = Note
    extra = 0  # Only shows if you want to add one

# --- Model Admins ---

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'priority', 'category', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    inlines = [SubTaskInline, NoteInline]
    # Groups fields into sections in the edit view
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
    list_display = ('title', 'status', 'parent_task_name')
    list_filter = ('status',)
    search_fields = ('title',)

    def parent_task_name(self, obj):
        return obj.task.title
    parent_task_name.short_description = 'Parent Task'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')  # Added color to list view
    search_fields = ('name',)

@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'color')  # Added level and color
    list_editable = ('level', 'color')         # Allow quick edits directly from the list
    search_fields = ('name',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('task', 'content_snippet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

    def content_snippet(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'