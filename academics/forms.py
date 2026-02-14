from django import forms
from .models import Class, Announcement, Assignment

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'code', 'description', 'semester', 'schedule', 'room']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MWF 9:00-10:00 AM'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Room 301'}),
        }
