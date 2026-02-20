from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RiskAssessment, TeacherConcern, WellnessCheckIn, Alert

@receiver(post_save, sender=RiskAssessment)
def create_risk_alert(sender, instance, created, **kwargs):
    """Create alert when student moves to high risk"""
    if instance.risk_level == 'high':
        # Check if alert already exists for this student
        existing_alert = Alert.objects.filter(
            student=instance.student,
            alert_type='high_risk',
            resolved=False
        ).exists()
        
        if not existing_alert:
            Alert.objects.create(
                student=instance.student,
                alert_type='high_risk',
                severity='critical',
                message=f'{instance.student.get_full_name()} has been identified as high risk. Risk score: {instance.risk_score}. GPA: {instance.gpa}, Attendance: {instance.attendance_rate}%, Missing assignments: {instance.missing_assignments}.'
            )

@receiver(post_save, sender=RiskAssessment)
def create_missing_assignments_alert(sender, instance, created, **kwargs):
    """Create alert when student has multiple missing assignments"""
    if instance.missing_assignments >= 3:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            student=instance.student,
            alert_type='missing_assignments',
            resolved=False
        ).exists()
        
        if not existing_alert:
            severity = 'high' if instance.missing_assignments >= 5 else 'medium'
            Alert.objects.create(
                student=instance.student,
                alert_type='missing_assignments',
                severity=severity,
                message=f'{instance.student.get_full_name()} has {instance.missing_assignments} missing assignments. Immediate follow-up recommended.'
            )

@receiver(post_save, sender=RiskAssessment)
def create_low_attendance_alert(sender, instance, created, **kwargs):
    """Create alert when student attendance drops below threshold"""
    if instance.attendance_rate and instance.attendance_rate < 75:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            student=instance.student,
            alert_type='low_attendance',
            resolved=False
        ).exists()
        
        if not existing_alert:
            severity = 'high' if instance.attendance_rate < 60 else 'medium'
            Alert.objects.create(
                student=instance.student,
                alert_type='low_attendance',
                severity=severity,
                message=f'{instance.student.get_full_name()} has low attendance rate of {instance.attendance_rate}%. Intervention may be needed.'
            )

@receiver(post_save, sender=TeacherConcern)
def create_teacher_concern_alert(sender, instance, created, **kwargs):
    """Create alert when teacher submits a concern"""
    if created:
        # Map teacher concern severity to alert severity
        severity_map = {'high': 'critical', 'medium': 'high', 'low': 'medium'}
        Alert.objects.create(
            student=instance.student,
            alert_type='teacher_concern',
            severity=severity_map.get(instance.severity, 'medium'),
            message=f'Teacher {instance.teacher.get_full_name()} reported a {instance.get_severity_display().lower()} severity {instance.get_concern_type_display().lower()} concern about {instance.student.get_full_name()}.'
        )

@receiver(post_save, sender=WellnessCheckIn)
def create_wellness_concern_alert(sender, instance, created, **kwargs):
    """Create alert when wellness check-in shows distress"""
    if created:
        # Check for concerning wellness indicators
        if instance.stress_level >= 4 or instance.motivation_level <= 2 or instance.need_help:
            severity = 'critical' if instance.need_help or instance.stress_level == 5 else 'high'
            Alert.objects.create(
                student=instance.student,
                alert_type='wellness_concern',
                severity=severity,
                message=f'{instance.student.get_full_name()} wellness check-in shows concerning indicators. Stress: {instance.stress_level}/5, Motivation: {instance.motivation_level}/5, Needs help: {"Yes" if instance.need_help else "No"}.'
            )
