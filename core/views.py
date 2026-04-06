from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import Task, Category, SubTask, Note 
from .forms import TaskForm
from django.http import HttpResponse
# --- Dashboard & Sidebar ---

def task_list(request):
    """Main dashboard with synchronized Quick Filters, Progress Bar, and Single-Row fetch."""
    tasks = Task.objects.all().select_related('category', 'priority').order_by('-created_at')
    categories = Category.objects.annotate(task_count=Count('tasks'))
    
    # 1. NEW: Single-Row Fetch (Handles the "Cancel" button or single row refresh)
    task_id = request.GET.get('id')
    if task_id:
        task = get_object_or_404(Task, id=task_id)
        return render(request, 'core/partials/task_rows.html', {'tasks': [task]})

    # 2. Filtering Logic
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    focus_mode = request.GET.get('focus') == 'true'
    search_query = request.GET.get('q') 
    
    if focus_mode:
        today = timezone.now().date()
        tasks = tasks.filter(
            Q(priority__name__icontains='High') | 
            Q(priority__name__icontains='Critical') | 
            Q(deadline__date__lte=today)
        ).exclude(status__iexact='Completed').distinct()
        
        if not tasks.exists():
            tasks = Task.objects.exclude(status__iexact='Completed').select_related('category', 'priority').order_by('-created_at')[:5]
    else:
        if status_filter: tasks = tasks.filter(status__iexact=status_filter)
        if category_filter: tasks = tasks.filter(category__name__iexact=category_filter)
            
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # 3. Global Progress (Calculated for the sidebar)
    total = Task.objects.count()
    done = Task.objects.filter(status__iexact='Completed').count()
    progress = int((done / total) * 100) if total > 0 else 0

    context = {
        'tasks': tasks, 
        'categories': categories, 
        'progress': progress, 
        'is_focus': focus_mode
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/task_rows.html', context)
    return render(request, 'core/dashboard.html', context)


def task_detail_sidebar(request, pk):
    """Loads content into the Right Side Panel."""
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'core/partials/task_detail_sidebar.html', {'task': task})


# --- Task CRUD ---

def task_create(request):
    """Handles new task creation via Modal."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            # Send empty response to close modal, trigger list refresh
            response = HttpResponse("")
            response["HX-Trigger"] = "taskListChanged"
            return response
    else:
        form = TaskForm()
    return render(request, 'core/partials/task_form.html', {'form': form, 'title': 'New Task'})


def task_edit(request, pk):
    """Handles both Modal Edit and Inline (Quick) Edit."""
    task = get_object_or_404(Task, pk=pk)
    is_inline = request.GET.get('inline') == 'true'

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            
            # If editing from the table directly (Inline)
            if is_inline:
                response = render(request, 'core/partials/task_rows.html', {'tasks': [task]})
                response["HX-Trigger"] = "taskListChanged"
                return response
            
            # If editing from the Modal
            response = HttpResponse("")
            response["HX-Trigger"] = "taskListChanged"
            return response
    else:
        form = TaskForm(instance=task)

    # Use specific template for Inline Edit vs Full Modal Edit
    template = 'core/partials/task_edit_form.html' if is_inline else 'core/partials/task_form.html'
    return render(request, template, {'form': form, 'task': task, 'title': 'Edit Task'})


@require_POST
def toggle_status(request, pk):
    """Cycles task status and returns the single updated row."""
    task = get_object_or_404(Task, pk=pk)
    cycle = {'Pending': 'In Progress', 'In Progress': 'Completed', 'Completed': 'Pending'}
    task.status = cycle.get(task.status, 'Pending')
    task.save()
    
    # Return just this row to avoid full table flicker
    response = render(request, 'core/partials/task_rows.html', {'tasks': [task]})
    response["HX-Trigger"] = "taskListChanged"
    return response


@require_http_methods(["DELETE", "POST"])
def task_delete(request, pk):
    """Deletes task and triggers global UI update."""
    get_object_or_404(Task, pk=pk).delete()
    response = HttpResponse("") 
    response["HX-Trigger"] = "taskListChanged"
    return response


# --- Subtasks (Real-time CRUD) ---

@require_POST
def add_subtask(request, task_pk):
    task = get_object_or_404(Task, task_pk)
    title = request.POST.get('subtask_title')
    if title:
        SubTask.objects.create(task=task, title=title, is_completed=False)
    return render(request, 'core/partials/subtask_section.html', {'task': task})


@require_POST
def toggle_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    subtask.is_completed = not subtask.is_completed
    subtask.save()
    
    task = subtask.task
    total = task.subtasks.count()
    done = task.subtasks.filter(is_completed=True).count()
    progress = int((done / total) * 100) if total > 0 else 0
    
    response = render(request, 'core/partials/progress_bar.html', {'progress': progress})
    response["HX-Trigger"] = "taskListChanged"
    return response


@require_http_methods(["DELETE", "POST"])
def delete_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk)
    subtask.delete()
    response = HttpResponse("")
    response["HX-Trigger"] = "taskListChanged"
    return response


# --- Notes (Autosave & Add) ---

@require_POST
def update_notes(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    task.notes = request.POST.get('notes', '')
    task.save()
    return HttpResponse(status=204)


@require_POST
def add_note(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    content = request.POST.get('note_content')
    if content:
        Note.objects.create(task=task, content=content)
    return render(request, 'core/partials/note_section.html', {'task': task})

def get_messages(request):
    # Sample data - in a real app, you'd pull this from a model
    samples = [
        {"user": "Alice", "text": "Can you check the roadmap?", "time": "2m ago"},
        {"user": "Bob", "text": "Budget files are uploaded.", "time": "1h ago"},
        {"user": "Charlie", "text": "Meeting at 3 PM.", "time": "4h ago"},
    ]
    
    html = ""
    for msg in samples:
        html += f'''
        <div class="px-4 py-3 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-50 last:border-0">
            <div class="flex justify-between items-start mb-1">
                <span class="text-[11px] font-black text-slate-900 uppercase tracking-tighter">{msg['user']}</span>
                <span class="text-[9px] font-medium text-slate-400">{msg['time']}</span>
            </div>
            <p class="text-[11px] text-slate-500 line-clamp-1">{msg['text']}</p>
        </div>
        '''
    return HttpResponse(html)

def get_notifications(request):
    # Sample data
    samples = [
        {"icon": "fa-check-circle", "color": "text-green-500", "text": "Task 'Homepage UI' completed"},
        {"icon": "fa-exclamation-circle", "color": "text-amber-500", "text": "Deadline approaching: API Integration"},
        {"icon": "fa-user-plus", "color": "text-blue-500", "text": "New team member joined"},
    ]
    
    html = ""
    for n in samples:
        html += f'''
        <div class="px-4 py-3 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-50 last:border-0 flex items-center gap-3">
            <i class="fa-solid {n['icon']} {n['color']} text-[12px]"></i>
            <p class="text-[11px] font-medium text-slate-600 tracking-tight">{n['text']}</p>
        </div>
        '''
    return HttpResponse(html)