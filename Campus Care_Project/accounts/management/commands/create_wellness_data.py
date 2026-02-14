from django.core.management.base import BaseCommand
from accounts.models import User
from wellness.models import WellnessCheckIn, RiskAssessment, Alert
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample wellness and risk assessment data'

    def handle(self, *args, **kwargs):
        students = User.objects.filter(role='student')
        
        for student in students:
            # Create wellness check-ins
            for i in range(3):
                WellnessCheckIn.objects.create(
                    student=student,
                    stress_level=random.randint(1, 5),
                    motivation_level=random.randint(1, 5),
                    workload_level=random.randint(1, 5),
                    sleep_quality=random.randint(1, 5),
                    need_help=random.choice([True, False])
                )
            
            # Create risk assessment
            risk_level = random.choice(['low', 'medium', 'high'])
            risk_score = {
                'low': random.uniform(0, 30),
                'medium': random.uniform(30, 60),
                'high': random.uniform(60, 100)
            }[risk_level]
            
            assessment = RiskAssessment.objects.create(
                student=student,
                risk_level=risk_level,
                risk_score=round(risk_score, 2),
                gpa=round(random.uniform(2.0, 4.0), 2),
                attendance_rate=round(random.uniform(70, 100), 2),
                missing_assignments=random.randint(0, 5)
            )
            
            # Create alert for high-risk students
            if risk_level == 'high':
                Alert.objects.create(
                    student=student,
                    alert_type='high_risk',
                    message=f'{student.get_full_name()} has been identified as high-risk. Risk score: {assessment.risk_score}'
                )
        
        self.stdout.write(self.style.SUCCESS('Sample wellness data created successfully!'))
