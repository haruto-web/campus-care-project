from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from accounts.models import User
from academics.models import Grade, Attendance, Assignment, Submission
from wellness.models import RiskAssessment, WellnessCheckIn, Alert
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Calculate risk assessments for all students'

    def handle(self, *args, **kwargs):
        students = User.objects.filter(role='student')
        
        for student in students:
            # Calculate GPA (Philippine 5.0 scale: 1.00 = Excellent, 5.00 = Failing)
            grades = Grade.objects.filter(student=student)
            if grades.exists():
                # Convert percentage to Philippine GPA scale
                avg_percentage = grades.aggregate(Avg('score'))['score__avg']
                if avg_percentage >= 97:
                    gpa = 1.00
                elif avg_percentage >= 94:
                    gpa = 1.25
                elif avg_percentage >= 91:
                    gpa = 1.50
                elif avg_percentage >= 88:
                    gpa = 1.75
                elif avg_percentage >= 85:
                    gpa = 2.00
                elif avg_percentage >= 82:
                    gpa = 2.25
                elif avg_percentage >= 79:
                    gpa = 2.50
                elif avg_percentage >= 76:
                    gpa = 2.75
                elif avg_percentage >= 75:
                    gpa = 3.00  # Passing grade
                else:
                    gpa = 5.00  # Failing
            else:
                gpa = 0
            
            # Calculate attendance rate
            attendance_records = Attendance.objects.filter(student=student)
            if attendance_records.exists():
                attendance_rate = (attendance_records.filter(status='present').count() / attendance_records.count()) * 100
            else:
                attendance_rate = 100
            
            # Count missing assignments
            student_classes = student.enrolled_classes.all()
            total_assignments = Assignment.objects.filter(class_obj__in=student_classes).count()
            submitted = Submission.objects.filter(student=student).count()
            missing_assignments = total_assignments - submitted
            
            # Calculate risk score
            risk_score = 0
            
            # GPA factor (0-40 points) - Philippine scale
            if gpa >= 4.0 or gpa == 5.0:  # Failing grades
                risk_score += 40
            elif gpa >= 3.5:  # Below average
                risk_score += 30
            elif gpa >= 3.0:  # Passing but concerning
                risk_score += 20
            elif gpa >= 2.5:  # Fair
                risk_score += 10
            # 1.0-2.25 = Good to Excellent (no risk points)
            
            # Attendance factor (0-30 points)
            if attendance_rate < 60:
                risk_score += 30
            elif attendance_rate < 70:
                risk_score += 25
            elif attendance_rate < 80:
                risk_score += 15
            elif attendance_rate < 90:
                risk_score += 5
            
            # Missing assignments factor (0-20 points)
            if missing_assignments >= 5:
                risk_score += 20
            elif missing_assignments >= 3:
                risk_score += 15
            elif missing_assignments >= 1:
                risk_score += 5
            
            # Wellness factor (0-10 points)
            recent_checkin = WellnessCheckIn.objects.filter(student=student).order_by('-date').first()
            if recent_checkin:
                if recent_checkin.stress_level >= 4 or recent_checkin.motivation_level <= 2 or recent_checkin.need_help:
                    risk_score += 10
            
            # Determine risk level
            if risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 30:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            # Create or update risk assessment
            RiskAssessment.objects.create(
                student=student,
                risk_level=risk_level,
                risk_score=risk_score,
                gpa=gpa,
                attendance_rate=attendance_rate,
                missing_assignments=missing_assignments
            )
            
            self.stdout.write(self.style.SUCCESS(f'Risk assessment calculated for {student.get_full_name()}: {risk_level} ({risk_score})'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully calculated risk assessments for {students.count()} students'))
