from django import forms
from .models import TeacherConcern, Intervention

class TeacherConcernForm(forms.ModelForm):
    class Meta:
        model = TeacherConcern
        fields = ['student', 'concern_type', 'severity', 'description', 'date_observed']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'concern_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'date_observed': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['student', 'intervention_type', 'description', 'scheduled_date', 'status', 'notes', 'outcome']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'intervention_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
