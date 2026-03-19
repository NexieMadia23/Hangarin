from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    # The hex code used in sidebar dots and table badges
    color = models.CharField(max_length=7, default="#64748b") 

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Priority(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#64748b")
    level = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = "Priorities"
        ordering = ['-level']

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('Starting', 'Starting'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Starting')
    deadline = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Used by the template to show the pulsing red warning."""
        if self.deadline and self.status != 'Done':
            return self.deadline < timezone.now()
        return False

    @property
    def subtask_progress(self):
        """Calculates percentage of completed subtasks."""
        total = self.subtasks.count()
        if total == 0:
            return 0
        completed = self.subtasks.filter(status=True).count()
        return int((completed / total) * 100)

class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=200)
    status = models.BooleanField(default=False)  # False = Pending, True = Completed

    def __str__(self):
        return f"{self.title} (Subtask of {self.task.title})"

class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.task.title}"