from django import forms
from .models import Class, Announcement, Assignment, Material

class ClassForm(forms.ModelForm):
    schedule_day = forms.ChoiceField(
        choices=[('', 'Select a day')] + Class.DAY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    schedule_time_range = forms.ChoiceField(
        choices=[('', 'Select a time range')] + Class.TIME_RANGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Class
        fields = ['name', 'code', 'section', 'year_level', 'description', 'semester', 'room']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MATH-7A'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Room 301'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        day, time_range = Class.parse_schedule(getattr(self.instance, 'schedule', ''))
        if day:
            self.fields['schedule_day'].initial = day
        if time_range:
            self.fields['schedule_time_range'].initial = time_range

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('schedule_day', '')
        time_range = cleaned_data.get('schedule_time_range', '')
        if any([day, time_range]) and not all([day, time_range]):
            message = 'Please select both a class day and a time range.'
            self.add_error('schedule_day', message)
            self.add_error('schedule_time_range', message)
        cleaned_data['schedule'] = Class.build_schedule(day, time_range)
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
