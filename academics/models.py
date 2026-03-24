from django.db import models
from django.conf import settings
from datetime import datetime

class Class(models.Model):
    YEAR_LEVEL_CHOICES = [
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
    ]
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classes_taught', null=True, blank=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_classes', blank=True)
    semester = models.CharField(max_length=50)
    schedule = models.CharField(max_length=200, blank=True, help_text='e.g., MWF 9:00-10:00 AM')
    room = models.CharField(max_length=50, blank=True)
    section = models.CharField(max_length=50, blank=True)
    year_level = models.CharField(max_length=2, choices=YEAR_LEVEL_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return f"{self.code} - {self.name}"

    @classmethod
    def parse_schedule(cls, schedule):
        if not schedule or ' | ' not in schedule:
            return [], '', ''
        day_part, time_range = schedule.split(' | ', 1)
        days = [day.strip() for day in day_part.split(',') if day.strip()]
        valid_days = {choice[0] for choice in cls.DAY_CHOICES}
        if not days or any(day not in valid_days for day in days):
            return [], '', ''
        if ' - ' not in time_range:
            return [], '', ''
        start_time, end_time = [part.strip() for part in time_range.split(' - ', 1)]
        if not cls._is_valid_time_display(start_time) or not cls._is_valid_time_display(end_time):
            return [], '', ''
        return days, cls._display_to_input_time(start_time), cls._display_to_input_time(end_time)

    @classmethod
    def build_schedule(cls, days, start_time, end_time):
        if not days or not start_time or not end_time:
            return ''
        display_days = ', '.join(days)
        return f'{display_days} | {cls._input_to_display_time(start_time)} - {cls._input_to_display_time(end_time)}'

    @staticmethod
    def _is_valid_time_display(value):
        try:
            datetime.strptime(value, '%I:%M %p')
            return True
        except ValueError:
            return False

    @staticmethod
    def _input_to_display_time(value):
        return datetime.strptime(value, '%H:%M').strftime('%I:%M %p')

    @staticmethod
    def _display_to_input_time(value):
        return datetime.strptime(value, '%I:%M %p').strftime('%H:%M')

class Assignment(models.Model):
    SUBMISSION_TYPE_CHOICES = [
        ('file_upload', 'File Upload'),
        ('text_entry', 'Text Entry'),
        ('both', 'File or Text'),
    ]
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_points = models.IntegerField()
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES, default='file_upload')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.class_obj.code}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    text_content = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['class_obj', 'student', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.class_obj.code} - {self.date}"

class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='grades')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.class_obj.code} - {self.score}/{self.max_score}"

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_school_wide = models.BooleanField(default=False, help_text='If True, visible to all users')
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_announcements', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.author.username}"

class Material(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='materials/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.class_obj.code}"
