from django.core.management.base import BaseCommand
from accounts.models import User
from wellness.models import WellnessCheckIn, Alert
from ml_models.gemini_client import GeminiClient
from ml_models.models import SentimentAnalysis
import time

class Command(BaseCommand):
    help = 'Create 10 test students with high/critical wellness check-ins'
    
    def handle(self, *args, **options):
        critical_comments = [
            "I feel hopeless and don't want to continue anymore. Everything is falling apart.",
            "I'm having thoughts of hurting myself. I can't take this pressure.",
            "Nobody cares about me. I feel worthless and alone.",
            "I want to give up on everything. Life feels meaningless.",
            "I can't handle this anymore. I'm breaking down completely.",
        ]
        
        high_comments = [
            "I'm extremely stressed and overwhelmed. I don't know what to do.",
            "Everything is too much. I feel like I'm drowning in work.",
            "I'm constantly anxious and can't sleep. This is unbearable.",
            "I feel like a failure. Nothing I do is good enough.",
            "I'm so depressed and exhausted. I need help desperately.",
        ]
        
        self.stdout.write("Creating 10 test students with critical/high distress...")
        
        client = GeminiClient()
        created = 0
        
        for i in range(10):
            username = f"teststudent{i+1}"
            
            # Check if user exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"Skipping {username} - already exists")
                continue
            
            # Create student
            student = User.objects.create_user(
                username=username,
                email=f"{username}@test.com",
                password="test123",
                first_name=f"Test{i+1}",
                last_name="Student",
                role='student',
                year_level=7 + (i % 4),
                profile_completed=True
            )
            
            # Create wellness check-in with critical/high distress
            if i < 5:
                # Critical distress
                comment = critical_comments[i]
                stress = 5
                motivation = 1
            else:
                # High distress
                comment = high_comments[i-5]
                stress = 5
                motivation = 1
            
            checkin = WellnessCheckIn.objects.create(
                student=student,
                stress_level=stress,
                motivation_level=motivation,
                workload_level=5,
                sleep_quality=1,
                need_help=True,
                text_response=comment
            )
            
            # Rate limiting
            if i > 0 and i % 15 == 0:
                self.stdout.write("Rate limit: waiting 60 seconds...")
                time.sleep(60)
            
            # Create alert for high/critical distress
            try:
                if i < 5:
                    Alert.objects.create(
                        student=student,
                        alert_type='emotional_distress',
                        severity='critical'
                    )
                    self.stdout.write(self.style.WARNING(f"[!] {student.username}: CRITICAL alert created"))
                    created += 1
                else:
                    Alert.objects.create(
                        student=student,
                        alert_type='emotional_distress',
                        severity='high'
                    )
                    self.stdout.write(self.style.WARNING(f"[!] {student.username}: HIGH alert created"))
                    created += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[X] Error: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"\nComplete! Created {created} students with high/critical alerts"
        ))
