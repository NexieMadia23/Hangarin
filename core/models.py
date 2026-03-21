from django.db import models
from django.utils import timezone

# 1. Create the Abstract Base Model as requested
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This ensures no table is created for BaseModel itself

# 2. Inherit BaseModel in all other models
class Category(BaseModel):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#64748b") 

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

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

class Task(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'), # Fixed the trailing space here
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    deadline = models.DateTimeField(null=True, blank=True)
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

class SubTask(BaseModel):
    # Requirement: Use field choices for status in SubTask too
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.title

    # For Admin requirement: Display parent_task_name
    @property
    def parent_task_name(self):
        return self.task.title

class Note(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()

    def __str__(self):
        return f"Note on {self.task.title}"