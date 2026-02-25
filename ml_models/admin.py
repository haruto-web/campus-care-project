from django.contrib import admin
from .models import PredictionLog, SentimentAnalysis

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'prediction_type', 'confidence', 'created_at']
    list_filter = ['prediction_type', 'created_at']
    search_fields = ['student__username', 'student__email']

@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['wellness_checkin', 'sentiment', 'alert_level', 'confidence', 'analyzed_at']
    list_filter = ['sentiment', 'alert_level', 'analyzed_at']
