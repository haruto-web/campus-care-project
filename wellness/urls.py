from django.urls import path
from . import views

app_name = 'wellness'

urlpatterns = [
    # Teacher Concerns
    path('concern/create/', views.create_concern, name='create_concern'),
    path('concern/create/<int:student_id>/', views.create_concern, name='create_concern_for_student'),
    path('concerns/', views.view_concerns, name='view_concerns'),
    
    # Counselor - At-Risk Students
    path('at-risk-students/', views.at_risk_students_list, name='at_risk_students'),
    
    # Counselor - Interventions
    path('intervention/create/', views.create_intervention, name='create_intervention'),
    path('intervention/create/<int:student_id>/', views.create_intervention, name='create_intervention_for_student'),
    path('interventions/', views.interventions_list, name='interventions_list'),
    path('intervention/<int:intervention_id>/update/', views.update_intervention, name='update_intervention'),
    
    # Counselor - Alerts
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alert/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    path('alert/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    
    # Counselor - Reports
    path('reports/', views.reports_view, name='reports'),
    path('generate-report/', views.generate_report, name='generate_report'),
    
    # API
    path('api/students/', views.api_students, name='api_students'),
]
