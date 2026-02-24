from wellness.models import WellnessCheckIn
from ml_models.models import SentimentAnalysis

print("\n=== SENTIMENT ANALYSIS RESULTS ===\n")

for checkin in WellnessCheckIn.objects.filter(comments__isnull=False).exclude(comments=''):
    print(f"Student: {checkin.student.get_full_name()}")
    print(f"Date: {checkin.date}")
    print(f"Stress: {checkin.stress_level}/5, Motivation: {checkin.motivation_level}/5")
    print(f"Need Help: {checkin.need_help}")
    print(f"Comments: {checkin.comments}")
    
    sa = SentimentAnalysis.objects.filter(wellness_checkin=checkin).first()
    if sa:
        print(f"\nAI Analysis:")
        print(f"  Sentiment: {sa.sentiment}")
        print(f"  Alert Level: {sa.alert_level}")
        print(f"  Confidence: {sa.confidence}")
        print(f"  Concerning Phrases: {sa.concerning_phrases}")
    
    print("\n" + "="*50 + "\n")
