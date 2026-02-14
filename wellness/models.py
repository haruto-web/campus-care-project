from django.db import models
from django.conf import settings

class WellnessCheckIn(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wellness_checkins')
    date = models.DateTimeField(auto_now_add=True)
    stress_level = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    motivation_level = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    workload_level = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    sleep_quality = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    need_help = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.date.strftime('%Y-%m-%d')}"

class RiskAssessment(models.Model):
    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='risk_assessments')
    date = models.DateField(auto_now_add=True)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    missing_assignments = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.risk_level} ({self.date})"

class TeacherConcern(models.Model):
    CONCERN_TYPES = [
        ('academic', 'Academic'),
        ('behavioral', 'Behavioral'),
        ('emotional', 'Emotional'),
        ('attendance', 'Attendance'),
    ]
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='concerns_received')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='concerns_submitted')
    concern_type = models.CharField(max_length=20, choices=CONCERN_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    description = models.TextField()
    date_observed = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.teacher.username} concern about {self.student.username} - {self.concern_type}"

class Intervention(models.Model):
    INTERVENTION_TYPES = [
        ('counseling', 'Counseling Session'),
        ('tutoring', 'Tutoring'),
        ('parent_meeting', 'Parent Meeting'),
        ('academic_plan', 'Academic Plan'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interventions')
    counselor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interventions_managed')
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPES)
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.intervention_type} for {self.student.username} - {self.status}"

class Alert(models.Model):
    ALERT_TYPES = [
        ('high_risk', 'High Risk Student'),
        ('missing_assignments', 'Missing Assignments'),
        ('low_attendance', 'Low Attendance'),
        ('wellness_concern', 'Wellness Concern'),
        ('teacher_concern', 'Teacher Concern'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.student.username}"
