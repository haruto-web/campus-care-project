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
