from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import User

@receiver(post_save, sender=User)
def create_risk_assessment_for_student(sender, instance, created, **kwargs):
    """Automatically create a risk assessment when a new student registers"""
    if created and instance.role == 'student':
        from wellness.models import RiskAssessment
        from academics.models import Attendance
        
        # Calculate initial stats
        attendance_records = Attendance.objects.filter(student=instance)
        if attendance_records.exists():
            attendance_rate = (attendance_records.filter(status='present').count() / attendance_records.count()) * 100
        else:
            attendance_rate = 100.0  # Default for new students
        
        # Create initial risk assessment with default values
        RiskAssessment.objects.create(
            student=instance,
            risk_level='low',  # Default to low risk for new students
            risk_score=0.0,
            gpa=0.0,
            attendance_rate=attendance_rate,
            missing_assignments=0,
            notes='Initial assessment created automatically'
        )


def _clear_other_sessions_for_user(user_id, keep_session_key=None):
    """Enforce one active device/session per account."""
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in active_sessions:
        data = session.get_decoded()
        if str(data.get('_auth_user_id')) != str(user_id):
            continue
        if keep_session_key and session.session_key == keep_session_key:
            continue
        session.delete()


@receiver(user_logged_in)
def enforce_single_device_session(sender, request, user, **kwargs):
    """
    When a user logs in on a new device/browser, expire previous sessions
    so only one device remains active for that account.
    """
    if not request.session.session_key:
        request.session.save()
    _clear_other_sessions_for_user(user.id, keep_session_key=request.session.session_key)
