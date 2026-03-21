from django import forms
from .models import Task, Category, Priority

class TaskForm(forms.ModelForm):
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
            'status': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] focus:border-transparent outline-none transition-all font-bold text-slate-700 cursor-pointer'
            }),
            'deadline': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#00c875]/20 outline-none font-medium'
                },
                format='%Y-%m-%dT%H:%M' # Crucial for 'datetime-local' to display existing data
            ),
            'priority': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] outline-none cursor-pointer'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] outline-none cursor-pointer'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Sync choices directly from the Model
        self.fields['status'].choices = Task.STATUS_CHOICES
        self.fields['status'].empty_label = None
        
        # 2. Standardize Category and Priority
        self.fields['category'].queryset = Category.objects.all()
        self.fields['priority'].queryset = Priority.objects.all()
        self.fields['category'].empty_label = "Select Category"
        self.fields['priority'].empty_label = "Select Priority"
        
        # 3. Form formatting for existing deadlines (Edit Mode)
        if self.instance and self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')

        # 4. Enforce 'Pending' as the initial state for all New Tasks
        if not self.instance.pk:
            self.initial['status'] = 'Pending'