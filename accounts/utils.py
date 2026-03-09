from academics.models import Attendance


def calculate_attendance_rate(student, class_obj=None):
    """Calculate attendance rate for a student, optionally filtered by class."""
    qs = Attendance.objects.filter(student=student)
    if class_obj:
        qs = qs.filter(class_obj=class_obj)
    total = qs.count()
    if total == 0:
        return None
    present = qs.filter(status='present').count()
    return round((present / total) * 100, 1)


def log_action(request_or_user, action, target_type='', target_id=None, target_label='', extra_data=None, ip=None):
    try:
        from accounts.models import AuditLog
        from django.http import HttpRequest

        actor = None
        ip_address = ip

        if isinstance(request_or_user, HttpRequest):
            actor = request_or_user.user if request_or_user.user.is_authenticated else None
            ip_address = ip_address or request_or_user.META.get('REMOTE_ADDR')
        else:
            actor = request_or_user

        AuditLog.objects.create(
            actor=actor,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            extra_data=extra_data or {},
            ip_address=ip_address,
        )
    except Exception:
        pass
