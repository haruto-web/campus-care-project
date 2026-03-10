from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('counselor', 'Counselor'),
        ('admin', 'Admin'),
    ]
    YEAR_LEVEL_CHOICES = [
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    ADMIN_ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('registrar', 'Registrar'),
        ('data_viewer', 'Data Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    admin_role = models.CharField(max_length=20, choices=ADMIN_ROLE_CHOICES, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    year_level = models.CharField(max_length=2, choices=YEAR_LEVEL_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    student_number = models.CharField(max_length=20, blank=True)
    section = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    id_picture = models.ImageField(upload_to='id_pictures/', blank=True, null=True)
    about_me = models.TextField(blank=True)
    profile_completed = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_occupation = models.CharField(max_length=100, blank=True)
    profile_skipped_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def get_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


class OTPCode(models.Model):
    contact_value = models.CharField(max_length=255)  # email
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate(cls, email):
        cls.objects.filter(contact_value=email, is_used=False).update(is_used=True)
        code = str(random.randint(100000, 999999))
        return cls.objects.create(contact_value=email, code=code)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=3)

    def __str__(self):
        return f"{self.contact_value} → {self.code}"


class ApprovedStudent(models.Model):
    student_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    year_level = models.CharField(max_length=2, choices=User.YEAR_LEVEL_CHOICES)
    section = models.CharField(max_length=50, blank=True)
    is_registered = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.student_number} — {self.last_name}, {self.first_name}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('USER_CREATED', 'User Created'),
        ('USER_DELETED', 'User Deleted'),
        ('USER_UPDATED', 'User Updated'),
        ('CLASS_CREATED', 'Class Created'),
        ('STUDENT_ENROLLED', 'Student Enrolled'),
        ('STUDENT_REMOVED_FROM_CLASS', 'Student Removed from Class'),
        ('ASSIGNMENT_CREATED', 'Assignment Created'),
        ('ASSIGNMENT_DELETED', 'Assignment Deleted'),
        ('SUBMISSION_GRADED', 'Submission Graded'),
        ('GRADE_CHANGED', 'Grade Changed'),
        ('CONCERN_SUBMITTED', 'Concern Submitted'),
        ('INTERVENTION_CREATED', 'Intervention Created'),
        ('INTERVENTION_UPDATED', 'Intervention Updated'),
        ('ALERT_RESOLVED', 'Alert Resolved'),
        ('REPORT_DOWNLOADED', 'Report Downloaded'),
        ('AI_USED', 'AI Used'),
        ('ADMIN_ROLE_CHANGED', 'Admin Role Changed'),
        ('MASS_DELETE', 'Mass Delete'),
    ]

    actor = models.ForeignKey(
        'User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='audit_logs'
    )
    action = models.CharField(max_length=40, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['actor']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.actor} — {self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"
