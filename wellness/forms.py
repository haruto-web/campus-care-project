from django import forms
from .models import TeacherConcern

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
