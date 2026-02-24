from django.core.management.base import BaseCommand
from accounts.models import User
from ml_models.gemini_client import GeminiClient
from ml_models.models import PredictionLog
from ml_models.utils import get_student_data_for_prediction
import time


class Command(BaseCommand):
    help = 'Run daily AI risk predictions for all students'
    
    def handle(self, *args, **options):
        client = GeminiClient()
        students = User.objects.filter(role='student', is_active=True)
        
        self.stdout.write(f"Starting AI predictions for {students.count()} students...")
        
        success_count = 0
        error_count = 0
        
        for i, student in enumerate(students):
            # Rate limiting: 15 requests per minute
            if i > 0 and i % 15 == 0:
                self.stdout.write("Rate limit: Waiting 60 seconds...")
                time.sleep(60)
            
            try:
                # Get student data
                data = get_student_data_for_prediction(student)
                
                # Predict risk (cached for 24h)
                result = client.predict_risk(data)
                
                # Save prediction
                PredictionLog.objects.create(
                    student=student,
                    prediction_type='risk',
                    prediction_value=result,
                    confidence=result.get('confidence', 0.8)
                )
                
                # Update student risk level
                student.risk_level = result['risk_level']
                student.save(update_fields=['risk_level'])
                
                success_count += 1
                self.stdout.write(f"[{i+1}/{students.count()}] {student.username}: {result['risk_level'].upper()}")
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"[{i+1}/{students.count()}] {student.username}: ERROR - {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"\nComplete! Success: {success_count}, Errors: {error_count}"))
