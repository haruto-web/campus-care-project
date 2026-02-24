from django.db import models
from accounts.models import User


class PredictionLog(models.Model):
    """Store all AI predictions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=50)
    prediction_value = models.JSONField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.prediction_type} - {self.created_at}"


class SentimentAnalysis(models.Model):
    """Sentiment analysis results for wellness check-ins"""
    wellness_checkin = models.OneToOneField('wellness.WellnessCheckIn', on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField()
    alert_level = models.CharField(max_length=20)
    concerning_phrases = models.JSONField(default=list)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.wellness_checkin.student.username} - {self.sentiment}"
