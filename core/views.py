from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.urls import reverse

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
    # Base QuerySet: Only show tasks belonging to the current user
    base_qs = Task.objects.filter(user=request.user).select_related('category', 'priority')

    # Category Sidebar: Only show categories that have tasks for THIS user
    categories = Category.objects.filter(tasks__user=request.user).annotate(
        task_count=Count('tasks', filter=Q(tasks__user=request.user))
    ).distinct()

    # 1. Single-Row Refresh (HTMX)
    task_id = request.GET.get('id')
    if task_id:
        task = get_object_or_404(base_qs, id=task_id)
        return render(request, 'core/partials/task_rows.html', {'tasks': [task], 'is_single': True})

    # 2. Filtering & Search Logic
    tasks_queryset = base_qs.order_by('-created_at')
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    focus_mode = request.GET.get('focus') == 'true'
    search_query = request.GET.get('q')

    if focus_mode:
        # Focus Mode: High Priority or Due Today
        today = timezone.now().date()
        tasks_queryset = tasks_queryset.filter(
            Q(priority__name__icontains='High') |
            Q(priority__name__icontains='Critical') |
            Q(deadline__date__lte=today)
        ).exclude(status__iexact='Completed').distinct()

        # Fallback: If no urgent tasks, show 5 most recent incomplete ones
        if not tasks_queryset.exists():
            tasks_queryset = base_qs.exclude(status__iexact='Completed').order_by('-created_at')[:5]
    else:
        if status_filter:
            tasks_queryset = tasks_queryset.filter(status__iexact=status_filter)
        if category_filter:
            tasks_queryset = tasks_queryset.filter(category__name__iexact=category_filter)

    if search_query:
        tasks_queryset = tasks_queryset.filter(title__icontains=search_query)

    # 3. Pagination (Infinite Scroll support)
    paginator = Paginator(tasks_queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 4. Global Progress Metric (Sidebar)
    total_count = base_qs.count()
    done_count = base_qs.filter(status__iexact='Completed').count()
    progress = int((done_count / total_count) * 100) if total_count > 0 else 0

    context = {
        'tasks': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'progress': progress,
        'is_focus': focus_mode,
        'search_query': search_query,
        'current_status': status_filter,
        'current_category': category_filter,
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
            task.user = request.user
            task.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response["HX-Redirect"] = reverse('core:task_list')
                return response
            return redirect('core:task_list')
    else:
        form = TaskForm()
    return render(request, 'core/partials/task_form.html', {'form': form, 'title': 'New Task'})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response["HX-Redirect"] = reverse('core:task_list')
                return response
            return redirect('core:task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'core/partials/task_form.html', {'form': form, 'task': task, 'title': 'Edit Task'})

@login_required
@require_POST
def toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    cycle = {'Pending': 'In Progress', 'In Progress': 'Completed', 'Completed': 'Pending'}
    task.status = cycle.get(task.status, 'Pending')
    task.save()
    
    response = render(request, 'core/partials/task_rows.html', {'tasks': [task], 'is_single': True})
    response["HX-Trigger"] = "taskListChanged"
    return response

@login_required
@require_http_methods(["DELETE", "POST"])
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse()
        response["HX-Redirect"] = reverse('core:task_list')
        return response
    return redirect('core:task_list')

# --- Details, Subtasks, Notes ---
@login_required
def task_detail_sidebar(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'core/partials/task_detail_sidebar.html', {'task': task})

@login_required
@require_POST
def add_subtask(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    title = request.POST.get('subtask_title')
    if title:
        SubTask.objects.create(task=task, title=title)
    return render(request, 'core/partials/subtask_section.html', {'task': task})

@login_required
@require_POST
def toggle_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk, task__user=request.user)
    subtask.is_completed = not subtask.is_completed
    subtask.save()
    response = HttpResponse(status=204)
    response["HX-Trigger"] = "taskListChanged"
    return response

@login_required
@require_http_methods(["DELETE", "POST"])
def delete_subtask(request, pk):
    subtask = get_object_or_404(SubTask, pk=pk, task__user=request.user)
    subtask.delete()
    response = HttpResponse("")
    response["HX-Trigger"] = "taskListChanged"
    return response

@login_required
@require_POST
def add_note(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    content = request.POST.get('note_content')
    if content:
        Note.objects.create(task=task, content=content)
    return render(request, 'core/partials/note_section.html', {'task': task})

@login_required
@require_POST
def update_notes(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    task.notes = request.POST.get('notes', '')
    task.save()
    return HttpResponse(status=204)

# --- Polling Endpoints ---
@login_required
def get_messages(request):
    samples = [{"user": "Hangarin Bot", "text": "Welcome to your new workspace!", "time": "Just now"}]
    html = "".join([
        f'<div class="px-4 py-3 hover:bg-slate-50 border-b last:border-0">'
        f'<div class="flex justify-between mb-1"><span class="text-[11px] font-black">{m["user"]}</span>'
        f'<span class="text-[9px] text-slate-400">{m["time"]}</span></div>'
        f'<p class="text-[11px] text-slate-500 line-clamp-1">{m["text"]}</p></div>'
        for m in samples
    ])
    return HttpResponse(html)

@login_required
def get_notifications(request):
    samples = [{"icon": "fa-circle-check", "color": "text-green-500", "text": "All systems operational"}]
    html = "".join([
        f'<div class="px-4 py-3 hover:bg-slate-50 flex items-center gap-3">'
        f'<i class="fa-solid {n["icon"]} {n["color"]} text-[12px]"></i>'
        f'<p class="text-[11px] font-medium text-slate-600 tracking-tight">{n["text"]}</p></div>'
        for n in samples
    ])
    return HttpResponse(html)