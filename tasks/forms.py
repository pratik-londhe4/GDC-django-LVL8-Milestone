
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from tasks.models import Report, Task

from .models import Task


class TaskCreateForm(LoginRequiredMixin, ModelForm):

    def clean_title(self):
        title = self.cleaned_data["title"]
        if(len(title) < 5):
            raise ValidationError("too small")
        return title.upper()

    def clean_priority(self):
        priority = self.cleaned_data["priority"]
        if(int(priority) < 0):
            raise ValidationError("Priority Cannot be Negative")
        return priority

    class Meta:
        model = Task
        fields = ("title", "description", "priority", "completed", )


class EmailReportForm(LoginRequiredMixin, ModelForm):
    class Meta:
        model = Report
        widgets = {
            'reminder_time': forms.TimeInput(
                attrs={'placeholder': 'HH:MM'}),
        }
        fields = ("reminder_time", )
    
   