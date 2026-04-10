from django import forms
from .models import Task, Category, Priority

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Ensure 'user' is EXCLUDED here so it doesn't show up in the form
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
                format='%Y-%m-%dT%H:%M'
            ),
            'priority': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] outline-none cursor-pointer'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-2.5 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-[#00c875] outline-none cursor-pointer'
            }),
        }

    def __init__(self, *args, **kwargs):
        # We pop the user out of the kwargs so we can filter the dropdowns
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['status'].choices = Task.STATUS_CHOICES
        self.fields['status'].empty_label = None
        
        # 1. Filter Category to only show global ones OR user-specific ones
        # If your Category model doesn't have a 'user' field yet, leave this as .all()
        self.fields['category'].queryset = Category.objects.all()
        self.fields['priority'].queryset = Priority.objects.all()
        
        self.fields['category'].empty_label = "Select Category"
        self.fields['priority'].empty_label = "Select Priority"
        
        if self.instance and self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')

        if not self.instance.pk:
            self.initial['status'] = 'Pending'