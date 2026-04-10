from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# 1. Base Abstract Model
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 2. Category Model
class Category(BaseModel):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#64748b")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# 3. Priority Model
class Priority(BaseModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#64748b")
    level = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Priority"
        verbose_name_plural = "Priorities"
        ordering = ['-level']

    def __str__(self):
        return self.name

# 4. Task Model (Crucial Updates Here)
class Task(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    # Added user field to fix FieldError
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Added notes field to match your update_notes view logic
    notes = models.TextField(blank=True, null=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.deadline and self.status != 'Completed':
            return timezone.now() > self.deadline
        return False

# 5. SubTask Model
class SubTask(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    is_completed = models.BooleanField(default=False) # Added for your toggle_subtask view

    def __str__(self):
        return self.title

    @property
    def parent_task_name(self):
        return self.task.title

# 6. Note Model (For individual note objects)
class Note(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_notes")
    content = models.TextField()

    def __str__(self):
        return f"Note on {self.task.title}"