from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import RiskAssessment, TeacherConcern, WellnessCheckIn, Alert, Intervention, Notification

@receiver(post_save, sender=RiskAssessment)
def create_risk_alert(sender, instance, created, **kwargs):
    """Create alert when student moves to high or critical risk"""
    if instance.risk_level in ['high', 'critical']:
        existing_alert = Alert.objects.filter(
            student=instance.student,
            alert_type='high_risk',
            resolved=False
        ).exists()
        if not existing_alert:
            severity = 'critical' if instance.risk_level == 'critical' else 'high'
            Alert.objects.create(
                student=instance.student,
                alert_type='high_risk',
                severity=severity,
                message=(
                    f'{instance.student.get_full_name()} has been identified as {instance.risk_level} risk. '
                    f'Risk score: {instance.risk_score}. '
                    f'GPA: {instance.gpa}, '
                    f'Attendance: {instance.attendance_rate}%, '
                    f'Missing assignments: {instance.missing_assignments}, '
                    f'Failing classes: {instance.failing_classes}.'
                )
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
        severity_map = {'high': 'critical', 'medium': 'high', 'low': 'medium'}
        Alert.objects.create(
            student=instance.student,
            alert_type='teacher_concern',
            severity=severity_map.get(instance.severity, 'medium'),
            message=f'Teacher {instance.teacher.get_full_name()} reported a {instance.get_severity_display().lower()} severity {instance.get_concern_type_display().lower()} concern about {instance.student.get_full_name()}.'
        )
        Notification.objects.create(
            recipient=instance.student,
            notif_type='teacher_concern',
            message=f'Your teacher {instance.teacher.get_full_name()} has raised a {instance.get_concern_type_display().lower()} concern about you. Please speak with your counselor if you need support.',
        )


@receiver(post_save, sender=Intervention)
def notify_student_intervention(sender, instance, created, **kwargs):
    """Notify student when an intervention is scheduled for them"""
    if instance.status == 'scheduled':
        local_sched = timezone.localtime(instance.scheduled_date)
        sched = local_sched.strftime('%b %d, %Y at %I:%M %p')
        msg = f'A {instance.get_intervention_type_display()} session has been scheduled for you on {sched} by {instance.counselor.get_full_name()}.'
        Notification.objects.create(
            recipient=instance.student,
            notif_type='intervention_scheduled',
            message=msg,
        )
        if instance.student.email:
            from accounts.otp_utils import send_transactional_email
            send_transactional_email(
                to_email=instance.student.email,
                subject='BrightTrack: Intervention Session Scheduled',
                text_content=(
                    f'Hi {instance.student.get_full_name()},\n\n'
                    f'{msg}\n\n'
                    f'Please log in to BrightTrack for more details.\n\n'
                    f'— BrightTrack Support Team'
                ),
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


@receiver(post_save, sender=RiskAssessment)
def create_failing_subjects_alert(sender, instance, created, **kwargs):
    """Create alert when student is failing 3 or more classes"""
    if instance.failing_classes >= 3:
        existing = Alert.objects.filter(
            student=instance.student,
            alert_type='failing_subjects',
            resolved=False
        ).exists()
        if not existing:
            severity = 'critical' if instance.failing_classes >= 5 else 'high'
            Alert.objects.create(
                student=instance.student,
                alert_type='failing_subjects',
                severity=severity,
                message=(
                    f'{instance.student.get_full_name()} is failing {instance.failing_classes} classes. '
                    f'Overall average maps to GPA {instance.gpa}. '
                    f'Consider subject-specific tutoring.'
                )
            )
