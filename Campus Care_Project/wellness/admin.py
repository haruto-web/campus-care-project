from django.contrib import admin
from .models import WellnessCheckIn, RiskAssessment, TeacherConcern, Intervention, Alert

@admin.register(WellnessCheckIn)
class WellnessCheckInAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'stress_level', 'motivation_level', 'need_help']
    list_filter = ['need_help', 'date']

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'risk_level', 'risk_score', 'date']
    list_filter = ['risk_level', 'date']

@admin.register(TeacherConcern)
class TeacherConcernAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher', 'concern_type', 'severity', 'date_observed', 'resolved']
    list_filter = ['concern_type', 'severity', 'resolved']

@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['student', 'counselor', 'intervention_type', 'scheduled_date', 'status']
    list_filter = ['intervention_type', 'status']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['student', 'alert_type', 'created_at', 'is_read', 'resolved']
    list_filter = ['alert_type', 'is_read', 'resolved']
