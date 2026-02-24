from django.core.management.base import BaseCommand
from wellness.models import WellnessCheckIn, Alert
from ml_models.gemini_client import GeminiClient
from ml_models.models import SentimentAnalysis
import time

class Command(BaseCommand):
    help = 'Analyze existing wellness check-ins with AI sentiment analysis'
    
    def handle(self, *args, **options):
        # Get check-ins with comments but no sentiment analysis
        checkins = WellnessCheckIn.objects.filter(
            comments__isnull=False
        ).exclude(comments='')
        
        # Filter out those already analyzed
        analyzed_ids = SentimentAnalysis.objects.values_list('wellness_checkin_id', flat=True)
        checkins = checkins.exclude(id__in=analyzed_ids)
        
        self.stdout.write(f"Found {checkins.count()} check-ins to analyze...")
        
        if checkins.count() == 0:
            self.stdout.write(self.style.SUCCESS("No check-ins to analyze!"))
            return
        
        client = GeminiClient()
        analyzed = 0
        alerts_created = 0
        
        for i, checkin in enumerate(checkins):
            # Rate limiting: 15 RPM = 1 request per 4 seconds
            if i > 0 and i % 15 == 0:
                self.stdout.write("Rate limit: waiting 60 seconds...")
                time.sleep(60)
            
            try:
                # Copy comments to text_response if empty
                if not checkin.text_response:
                    checkin.text_response = checkin.comments
                    checkin.save()
                
                # Analyze sentiment
                result = client.analyze_sentiment(checkin.comments)
                
                # Save analysis
                SentimentAnalysis.objects.create(
                    wellness_checkin=checkin,
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    alert_level=result['alert_level'],
                    concerning_phrases=result.get('concerning_phrases', [])
                )
                
                analyzed += 1
                
                # Create alert if high distress
                if result['alert_level'] in ['high', 'critical']:
                    Alert.objects.create(
                        student=checkin.student,
                        alert_type='emotional_distress',
                        severity='high',
                        description=f"Emotional distress detected in wellness check-in"
                    )
                    alerts_created += 1
                    self.stdout.write(self.style.WARNING(
                        f"[!] {checkin.student.get_full_name()}: {result['alert_level']} distress - Alert created"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"[OK] {checkin.student.get_full_name()}: {result['sentiment']} ({result['alert_level']})"
                    ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[X] Error analyzing check-in {checkin.id}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"\nAnalysis complete! Analyzed: {analyzed}, Alerts created: {alerts_created}"
        ))
