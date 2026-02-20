from django.core.management.base import BaseCommand
from accounts.models import User
from wellness.models import RiskAssessment
from academics.models import Attendance

class Command(BaseCommand):
    help = 'Create risk assessments for all students who don\'t have one'

    def handle(self, *args, **kwargs):
        students = User.objects.filter(role='student')
        created_count = 0
        
        for student in students:
            # Check if student already has a risk assessment
            if not RiskAssessment.objects.filter(student=student).exists():
                # Calculate attendance rate
                attendance_records = Attendance.objects.filter(student=student)
                if attendance_records.exists():
                    attendance_rate = (attendance_records.filter(status='present').count() / attendance_records.count()) * 100
                else:
                    attendance_rate = 100.0
                
                # Create risk assessment
                RiskAssessment.objects.create(
                    student=student,
                    risk_level='low',
                    risk_score=0.0,
                    gpa=0.0,
                    attendance_rate=attendance_rate,
                    missing_assignments=0,
                    notes='Initial assessment created by management command'
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created risk assessment for {student.get_full_name()}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal risk assessments created: {created_count}'))
