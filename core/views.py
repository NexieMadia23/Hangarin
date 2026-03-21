from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count  # Added Count for the sidebar badges
from .models import Task, Category     # Added Category import
from .forms import TaskForm

def task_list(request):
    """Main dashboard with Focus Mode, filtering, search, and category support."""
    tasks = Task.objects.all().select_related('category', 'priority').order_by('-created_at')
    
    # 1. Fetch Categories for the Sidebar (Dynamic from Admin)
    # We use annotate to count how many tasks are in each category
    categories = Category.objects.annotate(task_count=Count('tasks'))
    
    # 2. Grab filters from the URL
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    focus_mode = request.GET.get('focus') == 'true'
    search_query = request.GET.get('q') 
    
    # 3. Apply Filtering Logic
    if focus_mode:
        today = timezone.now().date()
        tasks = tasks.filter(
            Q(priority__name='High') | 
            (Q(deadline__date__lte=today) & ~Q(status='Done'))
        ).distinct()

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if category_filter:
        tasks = tasks.filter(category__name=category_filter)
        
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # 4. Progress Calculation
    total = Task.objects.count()
    done = Task.objects.filter(status='Done').count()
    progress = int((done / total) * 100) if total > 0 else 0

    context = {
        'tasks': tasks, 
        'categories': categories,  # THIS WAS MISSING - Now passed to HTML
        'progress': progress,
        'current_category': category_filter,
        'current_status': status_filter,
        'is_focus': focus_mode
    }
    
    # 5. HTMX Request handling
    if request.htmx:
        # If focusing, we need the whole main area; otherwise just the rows
        if 'focus' in request.GET:
             return render(request, 'core/dashboard.html', context)
        return render(request, 'core/partials/task_rows.html', context)
        
    return render(request, 'core/dashboard.html', context)

def task_create(request):
    """Handles creating a task via the modal."""
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
    """Handles editing a task via the modal."""
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            response = HttpResponse("")
            response["HX-Trigger"] = "taskListChanged"
            return response
    else:
        form = TaskForm(instance=task)
    return render(request, 'core/partials/task_form.html', {'form': form, 'title': 'Edit Task'})

@require_POST
def toggle_status(request, pk):
    """Cycles through statuses: Starting -> In Progress -> Review -> Done."""
    task = get_object_or_404(Task, pk=pk)
    cycle = {
        'Starting': 'In Progress', 
        'In Progress': 'Review', 
        'Review': 'Done', 
        'Done': 'Starting'
    }
    task.status = cycle.get(task.status, 'Starting')
    task.save()
    
    response = render(request, 'core/partials/task_rows.html', {'tasks': [task]})
    response["HX-Trigger"] = "taskListChanged"
    return response

@require_POST
def task_delete(request, pk):
    """Deletes task and refreshes board."""
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    response = HttpResponse("")
    response["HX-Trigger"] = "taskListChanged"
    return response