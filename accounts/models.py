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
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True)
    year_level = models.CharField(max_length=2, choices=YEAR_LEVEL_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    student_number = models.CharField(max_length=20, blank=True)
    section = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    id_picture = models.FileField(upload_to='id_pictures/', blank=True, null=True)
    about_me = models.TextField(blank=True)
    profile_completed = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_occupation = models.CharField(max_length=100, blank=True)
    profile_skipped_at = models.DateTimeField(blank=True, null=True)
    messaging_suspended_until = models.DateTimeField(blank=True, null=True)

    def is_messaging_suspended(self):
        if self.messaging_suspended_until:
            from django.utils import timezone
            return timezone.now() < self.messaging_suspended_until
        return False

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        full_name = super().get_full_name().strip()
        return full_name.title()
    
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


class RegistrationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    student_number = models.CharField(max_length=20)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    year_level = models.CharField(max_length=2, choices=User.YEAR_LEVEL_CHOICES)
    section = models.CharField(max_length=50, blank=True)
    password_hash = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='processed_registration_requests'
    )
    decided_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['student_number', 'email'], name='uniq_registration_request_student_email')
        ]

    def __str__(self):
        return f"{self.student_number} - {self.last_name}, {self.first_name} ({self.status})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('PROFILE_UPDATED', 'Profile Updated'),
        ('PROFILE_COMPLETED', 'Profile Completed'),
        ('REGISTRATION_SUBMITTED', 'Registration Submitted'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('USER_CREATED', 'User Created'),
        ('USER_DELETED', 'User Deleted'),
        ('USER_UPDATED', 'User Updated'),
        ('CLASS_CREATED', 'Class Created'),
        ('STUDENT_ENROLLED', 'Student Enrolled'),
        ('STUDENT_REMOVED_FROM_CLASS', 'Student Removed from Class'),
        ('ASSIGNMENT_CREATED', 'Assignment Created'),
        ('ASSIGNMENT_DELETED', 'Assignment Deleted'),
        ('MATERIAL_UPLOADED', 'Material Uploaded'),
        ('MATERIAL_DELETED', 'Material Deleted'),
        ('ATTENDANCE_MARKED', 'Attendance Marked'),
        ('SUBMISSION_GRADED', 'Submission Graded'),
        ('GRADE_CHANGED', 'Grade Changed'),
        ('MESSAGE_SENT', 'Message Sent'),
        ('MESSAGE_REPORTED', 'Message Reported'),
        ('MESSAGE_REPORT_RESOLVED', 'Message Report Resolved'),
        ('CONCERN_SUBMITTED', 'Concern Submitted'),
        ('INTERVENTION_CREATED', 'Intervention Created'),
        ('INTERVENTION_UPDATED', 'Intervention Updated'),
        ('ALERT_RESOLVED', 'Alert Resolved'),
        ('REPORT_DOWNLOADED', 'Report Downloaded'),
        ('STUDENT_PROFILE_VIEWED', 'Student Profile Viewed'),
        ('AUDIT_LOG_EXPORTED', 'Audit Log Exported'),
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
    previous_hash = models.CharField(max_length=64, blank=True, default='')
    entry_hash = models.CharField(max_length=64, blank=True, default='', db_index=True)
    signature_version = models.CharField(max_length=20, blank=True, default='hmac-sha256-v1')
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

    def delete(self, using=None, keep_parents=False):
        raise PermissionError('Audit log entries cannot be deleted through normal application flows.')
