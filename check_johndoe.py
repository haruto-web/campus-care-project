from wellness.models import Alert, WellnessCheckIn
from ml_models.models import SentimentAnalysis

print("\n=== JOHN DOE AI ANALYSIS STATUS ===\n")

john_checkin = WellnessCheckIn.objects.filter(student__username='johndoe').first()

if john_checkin:
    print(f"Wellness Check-in: YES")
    print(f"  Date: {john_checkin.date}")
    print(f"  Stress: {john_checkin.stress_level}/5")
    print(f"  Motivation: {john_checkin.motivation_level}/5")
    print(f"  Need Help: {john_checkin.need_help}")
    print(f"  Comments: {john_checkin.comments}")
    
    sa = SentimentAnalysis.objects.filter(wellness_checkin=john_checkin).first()
    if sa:
        print(f"\nAI Sentiment Analysis:")
        print(f"  Sentiment: {sa.sentiment}")
        print(f"  Alert Level: {sa.alert_level}")
        print(f"  Confidence: {sa.confidence}")
        print(f"  Concerning Phrases: {sa.concerning_phrases}")
    else:
        print("\nAI Sentiment Analysis: NOT FOUND")
else:
    print("Wellness Check-in: NO")

print(f"\n=== ALERTS FOR JOHN DOE ===\n")
alerts = Alert.objects.filter(student__username='johndoe')
print(f"Total Alerts: {alerts.count()}")
for alert in alerts:
    print(f"  - Type: {alert.alert_type}")
    print(f"    Severity: {alert.severity}")
    print(f"    Description: {alert.description}")
    print(f"    Created: {alert.created_at}")
    print(f"    Resolved: {alert.resolved}")
    print()
