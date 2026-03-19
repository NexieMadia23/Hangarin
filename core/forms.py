from django import forms
from .models import Task, Category, Priority

class TaskForm(forms.ModelForm):
    # Matches the exact cycle: Starting -> In Progress -> Review -> Done
    STATUS_CHOICES = [
        ('Starting', 'Starting'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Done', 'Done'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] focus:border-transparent outline-none transition-all font-bold text-slate-700 cursor-pointer'
        })
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'category', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'What needs to be done?',
                'class': 'w-full p-3 rounded-xl border border-slate-200 focus:border-[#00c875] focus:ring-2 focus:ring-[#00c875]/20 outline-none transition-all font-bold text-slate-700'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add more details...',
                'class': 'w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#00c875]/20 outline-none transition-all'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#00c875]/20 outline-none font-medium'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] outline-none cursor-pointer'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] outline-none cursor-pointer'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Refresh QuerySets to catch any new categories/priorities added in Admin
        self.fields['category'].queryset = Category.objects.all()
        self.fields['priority'].queryset = Priority.objects.all()
        self.fields['category'].empty_label = "Select Category"
        self.fields['priority'].empty_label = "Select Priority"
        
        # Enforce 'Starting' as the initial state for all New Tasks
        if not self.instance.pk:
            self.initial['status'] = 'Starting'