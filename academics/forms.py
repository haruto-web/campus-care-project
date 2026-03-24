from django import forms
from .models import Class, Announcement, Assignment, Material

class ClassForm(forms.ModelForm):
    schedule_days = forms.MultipleChoiceField(
        choices=Class.DAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    schedule_start_time = forms.TimeField(
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    schedule_end_time = forms.TimeField(
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    class Meta:
        model = Class
        fields = ['name', 'code', 'section', 'year_level', 'description', 'room']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MATH-7A'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Room 301'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        days, start_time, end_time = Class.parse_schedule(getattr(self.instance, 'schedule', ''))
        if days:
            self.fields['schedule_days'].initial = days
        if start_time:
            self.fields['schedule_start_time'].initial = start_time
        if end_time:
            self.fields['schedule_end_time'].initial = end_time

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('schedule_days') or []
        start_time = cleaned_data.get('schedule_start_time')
        end_time = cleaned_data.get('schedule_end_time')
        if any([days, start_time, end_time]) and not all([days, start_time, end_time]):
            message = 'Please select class day(s), start time, and end time.'
            self.add_error('schedule_days', message)
            self.add_error('schedule_start_time', message)
            self.add_error('schedule_end_time', message)
        if start_time and end_time and start_time >= end_time:
            self.add_error('schedule_end_time', 'End time must be later than start time.')
        cleaned_data['schedule'] = Class.build_schedule(
            days,
            start_time.strftime('%H:%M') if start_time else '',
            end_time.strftime('%H:%M') if end_time else '',
        )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.schedule = self.cleaned_data.get('schedule', '')
        if commit:
            instance.save()
        return instance

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'total_points', 'submission_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_points': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
            'submission_type': forms.Select(attrs={'class': 'form-control'}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
