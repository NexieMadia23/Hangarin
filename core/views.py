from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Task, Category, SubTask, Note
from .forms import TaskForm

# --- Public/Entrance ---
def home(request):
    if request.user.is_authenticated:
        return redirect('core:task_list')
    return render(request, 'account/signup.html')

# --- Dashboard & Sidebar ---
@login_required
def task_list(request):
    # 1. Base QuerySet - Changed to .all() so everyone sees everything
    all_tasks = Task.objects.all().select_related('category', 'priority')
    
    # 2. Sidebar Data - Annotate based on all tasks in the system
    categories = Category.objects.all().annotate(
        task_count=Count('tasks')
    )

    # 3. Handle Single Row Refresh (HTMX)
    task_id = request.GET.get('id')
    if task_id:
        task = get_object_or_404(all_tasks, id=task_id)
        return render(request, 'core/partials/task_rows.html', {'tasks': [task], 'is_single': True})

    # 4. Filtering Logic
    tasks_queryset = all_tasks.order_by('-created_at')
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    focus_mode = request.GET.get('focus') == 'true'
    search_query = request.GET.get('q')

    if focus_mode:
        today = timezone.now().date()
        tasks_queryset = tasks_queryset.filter(
            Q(priority__name__icontains='High') |
            Q(priority__name__icontains='Critical') |
            Q(deadline__date__lte=today)
        ).exclude(status__iexact='Completed').distinct()
    else:
        if status_filter:
            tasks_queryset = tasks_queryset.filter(status__iexact=status_filter)
        if category_filter:
            tasks_queryset = tasks_queryset.filter(category__name__iexact=category_filter)

    if search_query:
        tasks_queryset = tasks_queryset.filter(title__icontains=search_query)

    # 5. Pagination
    paginator = Paginator(tasks_queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 6. Progress Calculation (Global Progress)
    total_count = all_tasks.count()
    done_count = all_tasks.filter(status__iexact='Completed').count()
    progress = int((done_count / total_count) * 100) if total_count > 0 else 0

    context = {
        'tasks': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'progress': progress,
        'is_focus': focus_mode,
        'current_status': status_filter,
        'current_category': category_filter,
        'search_query': search_query,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/task_rows.html', context)

    return render(request, 'core/dashboard.html', context)

# --- Task CRUD ---
@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # We still assign the user as the 'creator', but others can see it
            task.user = request.user
            task.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse(status=204)
                response["HX-Trigger"] = "taskListChanged"
                return response
            return redirect('core:task_list')
    else:
        form = TaskForm()
    return render(request, 'core/partials/task_form.html', {'form': form, 'title': 'New Task'})

@login_required
def task_edit(request, pk):
    # Removed user=request.user so any logged-in user can edit
    task = get_object_or_404(Task, pk=pk)
    is_inline = request.GET.get('inline') == 'true'
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                if is_inline:
                    response = render(request, 'core/partials/task_rows.html', {'tasks': [task], 'is_single': True})
                else:
                    response = HttpResponse(status=204)
                
                response["HX-Trigger"] = "taskListChanged"
                return response
            return redirect('core:task_list')
    else:
        form = TaskForm(instance=task)
    
    template = 'core/partials/task_form_inline.html' if is_inline else 'core/partials/task_form.html'
    return render(request, template, {'form': form, 'task': task, 'title': 'Edit Task'})

@login_required
@require_POST
def toggle_status(request, pk):
    # Removed user=request.user
    task = get_object_or_404(Task, pk=pk)
    cycle = {'Pending': 'In Progress', 'In Progress': 'Completed', 'Completed': 'Pending'}
    task.status = cycle.get(task.status, 'Pending')
    task.save()
    
    response = render(request, 'core/partials/task_rows.html', {'tasks': [task], 'is_single': True})
    response["HX-Trigger"] = "taskListChanged"
    return response

@login_required
@require_http_methods(["DELETE", "POST"])
def task_delete(request, pk):
    # Removed user=request.user
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse("") 
        response["HX-Trigger"] = "taskListChanged"
        return response
    return redirect('core:task_list')

# --- Details, Subtasks, Notes ---
@login_required
def task_detail_sidebar(request, pk):
    # Removed user=request.user
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'core/partials/task_detail_sidebar.html', {'task': task})

@login_required
@require_POST
def add_subtask(request, task_pk):
    # Removed user=request.user
    task = get_object_or_404(Task, pk=task_pk)
    title = request.POST.get('subtask_title')
    if title:
        SubTask.objects.create(task=task, title=title)
    return render(request, 'core/partials/subtask_section.html', {'task': task})

@login_required
@require_POST
def toggle_subtask(request, pk):
    # Changed task__user filter to allow global access
    subtask = get_object_or_404(SubTask, pk=pk)
    subtask.is_completed = not subtask.is_completed
    subtask.save()
    response = HttpResponse(status=204)
    response["HX-Trigger"] = "taskListChanged"
    return response

@login_required
@require_http_methods(["DELETE", "POST"])
def delete_subtask(request, pk):
    # Changed task__user filter to allow global access
    subtask = get_object_or_404(SubTask, pk=pk)
    subtask.delete()
    response = HttpResponse("")
    response["HX-Trigger"] = "taskListChanged"
    return response

@login_required
@require_POST
def add_note(request, task_pk):
    # Removed user=request.user
    task = get_object_or_404(Task, pk=task_pk)
    content = request.POST.get('note_content')
    if content:
        Note.objects.create(task=task, content=content)
    return render(request, 'core/partials/note_section.html', {'task': task})

@login_required
@require_POST
def update_notes(request, task_pk):
    # Removed user=request.user
    task = get_object_or_404(Task, pk=task_pk)
    task.notes = request.POST.get('notes', '')
    task.save()
    return HttpResponse(status=204)

# --- Polling Endpoints ---
@login_required
def get_messages(request):
    return HttpResponse('<div class="px-4 py-3 text-[11px] text-slate-500">No new messages</div>')

@login_required
def get_notifications(request):
    return HttpResponse('<div class="px-4 py-3 text-[11px] text-slate-500">System operational</div>')