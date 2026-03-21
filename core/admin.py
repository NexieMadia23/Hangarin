from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Category, Priority, Task, SubTask, Note

# --- Custom Widget for Color Selection ---
class ColorPickerWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['type'] = 'color'  # Native browser color picker
        attrs['style'] = 'width: 100px; height: 40px; border: none; padding: 0;'
        return super().render(name, value, attrs, renderer)

# --- Inlines for a better Workflow ---

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ('title', 'status') 

class NoteInline(admin.StackedInline):
    model = Note
    extra = 0  

# --- Model Admins ---

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'priority', 'category')
    list_filter = ('status', 'priority', 'category')
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
    list_display = ('title', 'status', 'parent_task_name')
    list_filter = ('status',)
    search_fields = ('title',)

    def parent_task_name(self, obj):
        return obj.task.title
    parent_task_name.short_description = 'Parent Task Name'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview')
    search_fields = ('name',)

    def color_preview(self, obj):
        return format_html('<div style="width:30px; height:20px; background-color:{}; border-radius:4px; border:1px solid #ccc;"></div>', obj.color)
    color_preview.short_description = 'Color'

    # Use the color picker in the individual edit view
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'color':
            kwargs['widget'] = ColorPickerWidget
        return super().formfield_for_dbfield(db_field, **kwargs)

@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'color', 'preview')
    # Use list_editable carefully: ensure 'level' and 'color' aren't empty in DB
    list_editable = ('level', 'color')
    search_fields = ('name',)

    def preview(self, obj):
        return format_html('<div style="width:30px; height:20px; background-color:{}; border-radius:4px; border:1px solid #ccc;"></div>', obj.color)
    preview.short_description = 'Preview'

    # This makes the color picker show up in the Edit page
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'color':
            kwargs['widget'] = ColorPickerWidget
        return super().formfield_for_dbfield(db_field, **kwargs)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('task', 'content_snippet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

    def content_snippet(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'