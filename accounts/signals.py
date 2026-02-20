from django.db.models.signals import post_save
from django.dispatch import receiver
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
