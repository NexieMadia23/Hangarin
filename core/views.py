from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import Task, Category, SubTask, Note 
from .forms import TaskForm

def task_list(request):
    """Main dashboard with synchronized Quick Filters and Progress Bar."""
    # Start with all tasks and use select_related to speed up the database
    tasks = Task.objects.all().select_related('category', 'priority').order_by('-created_at')
    categories = Category.objects.annotate(task_count=Count('tasks'))
    
    # 1. Grab filters (FIXED: Defined these before using them)
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    focus_mode = request.GET.get('focus') == 'true'
    search_query = request.GET.get('q') 
    
    # 2. Filtering Logic
    if focus_mode:
        today = timezone.now().date()
        # Look for "High" or "Critical" in priority OR overdue tasks
        tasks = tasks.filter(
            Q(priority__name__icontains='High') | 
            Q(priority__name__icontains='Critical') | 
            Q(deadline__date__lte=today)
        ).exclude(status__iexact='Completed').distinct()
        
        # FALLBACK: If Focus Mode is empty, show the 5 most recent incomplete tasks
        if not tasks.exists():
            tasks = Task.objects.exclude(status__iexact='Completed').select_related('category', 'priority').order_by('-created_at')[:5]

    # Apply Standard Filters ONLY if NOT in focus mode
    else:
        if status_filter:
            tasks = tasks.filter(status__iexact=status_filter)
        
        if category_filter:
            tasks = tasks.filter(category__name__iexact=category_filter)
            
    # Search is applied regardless of Focus Mode
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # 3. Progress Calculation (Safe for empty databases)
    total = Task.objects.count()
    done = Task.objects.filter(status__iexact='Completed').count()
    progress = int((done / total) * 100) if total > 0 else 0

    context = {
        'tasks': tasks, 
        'categories': categories,
        'progress': progress,
        'is_focus': focus_mode
    }
    
    # 4. HTMX Request handling
    if hasattr(request, 'htmx') and request.htmx:
        return render(request, 'core/partials/task_rows.html', context)
        
    return render(request, 'core/dashboard.html', context)

# --- Task Actions (Create, Edit, Delete, Toggle) ---

def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse("")
            response["HX-Trigger"] = "taskListChanged"
            return response
    else:
        form = TaskForm()
    return render(request, 'core/partials/task_form.html', {'form': form, 'title': 'New Task'})

def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.GET.get('inline') == 'true':
                return render(request, 'core/partials/task_rows.html', {'tasks': [task]})
            
            response = HttpResponse("")
            response["HX-Trigger"] = "taskListChanged"
            return response
    else:
        form = TaskForm(instance=task)
    
    template = 'core/partials/task_edit_form.html' if request.GET.get('inline') == 'true' else 'core/partials/task_form.html'
    return render(request, template, {'form': form, 'task': task, 'title': 'Edit Task'})

@require_POST
def toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    cycle = {'Pending': 'In Progress', 'In Progress': 'Completed', 'Completed': 'Pending'}
    task.status = cycle.get(task.status, 'Pending')
    task.save()
    
    response = render(request, 'core/partials/task_rows.html', {'tasks': [task]})
    response["HX-Trigger"] = "taskListChanged"
    return response

@require_http_methods(["DELETE", "POST"])
def task_delete(request, pk):
    get_object_or_404(Task, pk=pk).delete()
    response = HttpResponse("") 
    response["HX-Trigger"] = "taskListChanged"
    return response

# --- Subtasks & Notes ---

@require_POST
def add_subtask(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    title = request.POST.get('subtask_title')
    if title:
        SubTask.objects.create(task=task, title=title, status='Pending')
    return render(request, 'core/partials/subtask_section.html', {'task': task})

@require_POST
def add_note(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    content = request.POST.get('note_content')
    if content:
        Note.objects.create(task=task, content=content)
    return render(request, 'core/partials/note_section.html', {'task': task})