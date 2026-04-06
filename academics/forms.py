import json

from django import forms

from .models import Class, Announcement, Assignment, Material


class ClassForm(forms.ModelForm):
    schedule_blocks = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
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
        self.fields['schedule_blocks'].initial = json.dumps(
            Class.parse_schedule_blocks(getattr(self.instance, 'schedule', ''))
        )

    def clean(self):
        cleaned_data = super().clean()
        raw_schedule_blocks = cleaned_data.get('schedule_blocks') or '[]'

        try:
            schedule_blocks = json.loads(raw_schedule_blocks)
        except (TypeError, ValueError):
            raise forms.ValidationError('Invalid schedule data.')

        if not isinstance(schedule_blocks, list):
            raise forms.ValidationError('Invalid schedule data.')

        valid_days = {choice[0] for choice in Class.DAY_CHOICES}
        normalized_blocks = []

        for block in schedule_blocks:
            if not isinstance(block, dict):
                raise forms.ValidationError('Invalid schedule entry.')

            days = [day for day in (block.get('days') or []) if day]
            start_time = (block.get('start_time') or '').strip()
            end_time = (block.get('end_time') or '').strip()
            classroom = (block.get('classroom') or '').strip()

            if not any([days, start_time, end_time]):
                continue

            if not all([days, start_time, end_time]):
                self.add_error('schedule_blocks', 'Each schedule entry must include class day(s), start time, and end time.')
                continue

            if any(day not in valid_days for day in days):
                self.add_error('schedule_blocks', 'Invalid class day selected.')
                continue

            try:
                Class._input_to_display_time(start_time)
                Class._input_to_display_time(end_time)
            except ValueError:
                self.add_error('schedule_blocks', 'Invalid schedule time selected.')
                continue

            if start_time >= end_time:
                self.add_error('schedule_blocks', 'Each schedule entry must end after it starts.')
                continue

            normalized_blocks.append({
                'days': days,
                'start_time': start_time,
                'end_time': end_time,
                'classroom': classroom,
            })

        overlap_error = self._first_schedule_overlap_error(normalized_blocks)
        if overlap_error:
            self.add_error('schedule_blocks', overlap_error)

        cleaned_data['schedule'] = Class.build_schedule_blocks(normalized_blocks)
        cleaned_data['schedule_blocks'] = json.dumps(normalized_blocks)
        return cleaned_data

    def _first_schedule_overlap_error(self, blocks):
        for i in range(len(blocks)):
            first = blocks[i]
            first_days = set(first.get('days') or [])
            first_start = first.get('start_time', '')
            first_end = first.get('end_time', '')
            for j in range(i + 1, len(blocks)):
                second = blocks[j]
                second_days = set(second.get('days') or [])
                second_start = second.get('start_time', '')
                second_end = second.get('end_time', '')

                if not (first_days & second_days):
                    continue

                if first_start < second_end and first_end > second_start:
                    shared_days = sorted(first_days & second_days)
                    shared_days_text = ', '.join(shared_days)
                    return (
                        f'Conflict warning: Schedule {i + 1} overlaps with Schedule {j + 1} '
                        f'on {shared_days_text}. Please adjust the times.'
                    )
        return None

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.schedule = self.cleaned_data.get('schedule', '')
        if commit:
            instance.save()
        return instance


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'available_at', 'due_date', 'total_points', 'submission_type', 'max_attempts']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'available_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_points': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
            'submission_type': forms.Select(attrs={'class': 'form-control'}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
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
