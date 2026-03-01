from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import TeacherConcern, Intervention, Alert, RiskAssessment, WellnessCheckIn
from .forms import TeacherConcernForm, InterventionForm
from accounts.models import User

@login_required
def create_concern(request, student_id=None):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can report concerns.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherConcernForm(request.POST)
        if form.is_valid():
            concern = form.save(commit=False)
            concern.teacher = request.user
            concern.save()
            messages.success(request, f'Concern about {concern.student.get_full_name()} reported successfully!')
            return redirect('wellness:view_concerns')
    else:
        if student_id:
            student = get_object_or_404(User, id=student_id, role='student')
            form = TeacherConcernForm(initial={'student': student})
        else:
            form = TeacherConcernForm()
        
        # Filter students to only show those in teacher's classes
        from academics.models import Class
        teacher_classes = Class.objects.filter(teacher=request.user)
        student_ids = []
        for cls in teacher_classes:
            student_ids.extend(cls.students.values_list('id', flat=True))
        form.fields['student'].queryset = User.objects.filter(id__in=student_ids, role='student')
    
    return render(request, 'wellness/create_concern.html', {'form': form})

@login_required
def view_concerns(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    concerns = TeacherConcern.objects.filter(teacher=request.user).order_by('-created_at')
    
    context = {
        'concerns': concerns,
    }
    return render(request, 'wellness/view_concerns.html', context)

# Counselor Views
@login_required
def at_risk_students_list(request):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    # Get all students with risk assessments
    risk_assessments = RiskAssessment.objects.select_related('student').order_by('-risk_score')
    
    # Apply filters
    risk_filter = request.GET.get('risk_level', '')
    search_query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')
    
    if risk_filter:
        risk_assessments = risk_assessments.filter(risk_level=risk_filter)
    
    if search_query:
        risk_assessments = risk_assessments.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__email__icontains=search_query)
        )
    
    if year_level_filter:
        risk_assessments = risk_assessments.filter(student__year_level=year_level_filter)
    
    # Prepare student data
    students_data = []
    for assessment in risk_assessments:
        students_data.append({
            'student': assessment.student,
            'risk_level': assessment.risk_level,
            'risk_score': assessment.risk_score,
            'gpa': assessment.gpa,
            'attendance_rate': assessment.attendance_rate,
            'missing_assignments': assessment.missing_assignments,
        })
    
    context = {
        'students': students_data,
        'risk_filter': risk_filter,
        'search_query': search_query,
        'year_level_filter': year_level_filter,
    }
    return render(request, 'wellness/at_risk_students.html', context)

@login_required
def create_intervention(request, student_id=None):
    if request.user.role not in ['counselor', 'admin', 'teacher']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    # Get AI recommendations if student_id provided
    ai_recommendations = None
    selected_student = None
    if student_id:
        selected_student = get_object_or_404(User, id=student_id, role='student')
        risk_assessment = RiskAssessment.objects.filter(student=selected_student).order_by('-date').first()
        
        if risk_assessment and risk_assessment.risk_level in ['medium', 'high']:
            try:
                from ml_models.gemini_client import GeminiClient
                from ml_models.utils import get_student_profile_for_intervention
                
                client = GeminiClient()
                profile = get_student_profile_for_intervention(selected_student)
                result = client.recommend_intervention(profile)
                ai_recommendations = result.get('recommendations', [])
            except:
                pass
    
    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.counselor = request.user
            intervention.save()
            messages.success(request, f'Intervention for {intervention.student.get_full_name()} created successfully!')
            return redirect('wellness:interventions_list')
    else:
        if student_id:
            form = InterventionForm(initial={'student': selected_student})
        else:
            form = InterventionForm()
        
        form.fields['student'].queryset = User.objects.filter(role='student')
    
    # Statistics
    total_students = User.objects.filter(role='student').count()
    high_risk_count = RiskAssessment.objects.filter(risk_level='high').values('student').distinct().count()
    unresolved_alerts = Alert.objects.filter(resolved=False, severity__in=['critical', 'high']).count()
    pending_interventions = Intervention.objects.filter(status='scheduled').count()
    
    context = {
        'form': form,
        'total_students': total_students,
        'high_risk_count': high_risk_count,
        'unresolved_alerts': unresolved_alerts,
        'pending_interventions': pending_interventions,
        'ai_recommendations': ai_recommendations,
        'selected_student': selected_student,
    }
    return render(request, 'wellness/create_intervention.html', context)

@login_required
def interventions_list(request):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    interventions = Intervention.objects.select_related('student', 'counselor').order_by('-scheduled_date')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    year_level_filter = request.GET.get('year_level', '')
    
    if status_filter == 'history':
        interventions = interventions.filter(status__in=['completed', 'cancelled'])
    elif status_filter:
        interventions = interventions.filter(status=status_filter)
    
    if year_level_filter:
        interventions = interventions.filter(student__year_level=year_level_filter)
    
    context = {
        'interventions': interventions,
        'status_filter': status_filter,
        'year_level_filter': year_level_filter,
    }
    return render(request, 'wellness/interventions_list.html', context)

@login_required
def update_intervention(request, intervention_id):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    intervention = get_object_or_404(Intervention, id=intervention_id)
    
    if request.method == 'POST':
        form = InterventionForm(request.POST, instance=intervention)
        if form.is_valid():
            form.save()
            messages.success(request, 'Intervention updated successfully!')
            return redirect('wellness:interventions_list')
    else:
        form = InterventionForm(instance=intervention)
        form.fields['student'].queryset = User.objects.filter(role='student')
    
    context = {
        'form': form,
        'intervention': intervention,
    }
    return render(request, 'wellness/update_intervention.html', context)

@login_required
def alerts_list(request):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    alerts = Alert.objects.select_related('student').order_by('-created_at')
    
    # Apply filters
    alert_type = request.GET.get('type', '')
    show_resolved = request.GET.get('resolved', '')
    severity_filter = request.GET.get('severity', '')
    
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    
    if show_resolved != 'true':
        alerts = alerts.filter(resolved=False)
    
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    
    # Count unread critical/high severity alerts for warning
    critical_unread = Alert.objects.filter(severity='critical', is_read=False, resolved=False).count()
    high_unread = Alert.objects.filter(severity='high', is_read=False, resolved=False).count()
    
    context = {
        'alerts': alerts,
        'alert_type': alert_type,
        'show_resolved': show_resolved,
        'severity_filter': severity_filter,
        'critical_unread': critical_unread,
        'high_unread': high_unread,
    }
    return render(request, 'wellness/alerts_list.html', context)

@login_required
def bulk_create_interventions(request):
    from django.utils import timezone as tz
    from datetime import timedelta as td
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    # Get all students with unresolved critical/high alerts who don't have a scheduled intervention
    urgent_alerts = Alert.objects.filter(
        severity__in=['critical', 'high'],
        resolved=False
    ).select_related('student').values_list('student', flat=True).distinct()

    students = User.objects.filter(id__in=urgent_alerts, role='student')
    created_count = 0

    for student in students:
        # Skip if already has a scheduled intervention
        if Intervention.objects.filter(student=student, status='scheduled').exists():
            continue

        risk = RiskAssessment.objects.filter(student=student).order_by('-date').first()
        intervention_type = 'counseling'
        if risk and risk.missing_assignments >= 3:
            intervention_type = 'tutoring'

        Intervention.objects.create(
            student=student,
            counselor=request.user,
            intervention_type=intervention_type,
            description=f'Auto-created intervention for {student.get_full_name()} due to critical/high risk alert.',
            scheduled_date=tz.now() + td(days=1),
            status='scheduled',
        )
        # Mark this student's critical/high alerts as read
        Alert.objects.filter(
            student=student,
            severity__in=['critical', 'high'],
            resolved=False
        ).update(is_read=True)
        created_count += 1

    if created_count > 0:
        messages.success(request, f'✅ Done! {created_count} intervention(s) created and alerts marked as read.')
    else:
        messages.info(request, 'All critical/high risk students already have scheduled interventions.')

    return redirect('wellness:alerts_list')


@login_required
def mark_alert_read(request, alert_id):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    alert = get_object_or_404(Alert, id=alert_id)
    alert.is_read = True
    alert.save()
    
    from django.urls import reverse
    params = request.GET.urlencode()
    url = reverse('wellness:alerts_list')
    return redirect(f'{url}?{params}' if params else url)

@login_required
def resolve_alert(request, alert_id):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    alert = get_object_or_404(Alert, id=alert_id)
    alert.resolved = True
    alert.is_read = True
    alert.save()
    
    from django.urls import reverse
    params = request.GET.urlencode()
    url = reverse('wellness:alerts_list')
    return redirect(f'{url}?{params}' if params else url)

@login_required
def reports_view(request):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    # Risk level counts
    high_risk_count = RiskAssessment.objects.filter(risk_level='high').values('student').distinct().count()
    medium_risk_count = RiskAssessment.objects.filter(risk_level='medium').values('student').distinct().count()
    low_risk_count = RiskAssessment.objects.filter(risk_level='low').values('student').distinct().count()
    total_students = User.objects.filter(role='student').count()
    
    # Intervention statistics
    scheduled_interventions = Intervention.objects.filter(status='scheduled').count()
    completed_interventions = Intervention.objects.filter(status='completed').count()
    cancelled_interventions = Intervention.objects.filter(status='cancelled').count()
    total_interventions = Intervention.objects.count()
    completion_rate = round((completed_interventions / total_interventions * 100), 1) if total_interventions > 0 else 0
    
    # Alert statistics
    unresolved_alerts = Alert.objects.filter(resolved=False).count()
    resolved_alerts = Alert.objects.filter(resolved=True).count()
    total_alerts = Alert.objects.count()
    resolution_rate = round((resolved_alerts / total_alerts * 100), 1) if total_alerts > 0 else 0
    
    # Alerts by type
    alerts_by_type = []
    for choice in Alert.ALERT_TYPES:
        count = Alert.objects.filter(alert_type=choice[0]).count()
        if count > 0:
            alerts_by_type.append({'type_display': choice[1], 'count': count})
    
    # Interventions by type
    interventions_by_type = []
    for choice in Intervention.INTERVENTION_TYPES:
        count = Intervention.objects.filter(intervention_type=choice[0]).count()
        if count > 0:
            interventions_by_type.append({'type_display': choice[1], 'count': count})
    
    # Academic statistics (removed avg_gpa)
    latest_assessments = RiskAssessment.objects.filter(
        id__in=RiskAssessment.objects.values('student').annotate(latest=Count('id')).values('latest')
    )
    avg_attendance = latest_assessments.aggregate(Avg('attendance_rate'))['attendance_rate__avg']
    
    total_concerns = TeacherConcern.objects.count()
    total_checkins = WellnessCheckIn.objects.count()
    
    # Age range analysis for high-risk students
    high_risk_students = User.objects.filter(
        risk_assessments__risk_level='high',
        date_of_birth__isnull=False
    ).distinct()
    
    age_ranges = {
        '15-17': 0,
        '18-20': 0,
        '21-23': 0,
        '24+': 0
    }
    
    for student in high_risk_students:
        age = student.get_age()
        if age:
            if 15 <= age <= 17:
                age_ranges['15-17'] += 1
            elif 18 <= age <= 20:
                age_ranges['18-20'] += 1
            elif 21 <= age <= 23:
                age_ranges['21-23'] += 1
            elif age >= 24:
                age_ranges['24+'] += 1
    
    # Find most problematic age range
    most_problematic_age = max(age_ranges, key=age_ranges.get) if any(age_ranges.values()) else None
    
    # Prepare age range data for chart
    age_range_values = [age_ranges['15-17'], age_ranges['18-20'], age_ranges['21-23'], age_ranges['24+']]
    
    # Recent activity
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_concerns = TeacherConcern.objects.filter(
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:10]
    
    upcoming_interventions = Intervention.objects.filter(
        status='scheduled',
        scheduled_date__gte=datetime.now()
    ).order_by('scheduled_date')[:10]
    
    # Data for charts
    risk_distribution_data = {
        'labels': ['High Risk', 'Medium Risk', 'Low Risk'],
        'data': [high_risk_count, medium_risk_count, low_risk_count]
    }
    
    intervention_status_data = {
        'labels': ['Scheduled', 'Completed', 'Cancelled'],
        'data': [scheduled_interventions, completed_interventions, cancelled_interventions]
    }
    
    context = {
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'total_students': total_students,
        'scheduled_interventions': scheduled_interventions,
        'completed_interventions': completed_interventions,
        'cancelled_interventions': cancelled_interventions,
        'total_interventions': total_interventions,
        'completion_rate': completion_rate,
        'unresolved_alerts': unresolved_alerts,
        'resolved_alerts': resolved_alerts,
        'total_alerts': total_alerts,
        'resolution_rate': resolution_rate,
        'alerts_by_type': alerts_by_type,
        'interventions_by_type': interventions_by_type,
        'avg_attendance': round(avg_attendance, 1) if avg_attendance else 'N/A',
        'total_concerns': total_concerns,
        'total_checkins': total_checkins,
        'recent_concerns': recent_concerns,
        'upcoming_interventions': upcoming_interventions,
        'age_ranges': age_ranges,
        'age_range_values': age_range_values,
        'most_problematic_age': most_problematic_age,
        'risk_distribution_data': risk_distribution_data,
        'intervention_status_data': intervention_status_data,
    }
    return render(request, 'wellness/reports.html', context)

@login_required
def generate_report(request):
    if request.user.role not in ['counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    
    # Get all data for report
    high_risk_students = RiskAssessment.objects.filter(risk_level='high').select_related('student')
    medium_risk_students = RiskAssessment.objects.filter(risk_level='medium').select_related('student')
    
    # Statistics
    high_risk_count = high_risk_students.count()
    medium_risk_count = medium_risk_students.count()
    low_risk_count = RiskAssessment.objects.filter(risk_level='low').count()
    
    scheduled_interventions = Intervention.objects.filter(status='scheduled').count()
    completed_interventions = Intervention.objects.filter(status='completed').count()
    
    unresolved_alerts = Alert.objects.filter(resolved=False).count()
    
    # Recent concerns
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_concerns = TeacherConcern.objects.filter(created_at__gte=seven_days_ago).select_related('student', 'teacher')
    
    context = {
        'generated_date': datetime.now(),
        'generated_by': request.user.get_full_name(),
        'high_risk_students': high_risk_students,
        'medium_risk_students': medium_risk_students,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'scheduled_interventions': scheduled_interventions,
        'completed_interventions': completed_interventions,
        'unresolved_alerts': unresolved_alerts,
        'recent_concerns': recent_concerns,
    }
    
    html = render_to_string('wellness/report_template.html', context)
    response = HttpResponse(html, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="campus_care_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html"'
    return response

@login_required
def api_students(request):
    """API endpoint to get all students for search"""
    if request.user.role not in ['counselor', 'admin', 'teacher']:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from django.http import JsonResponse
    students = User.objects.filter(role='student').values(
        'id', 'first_name', 'last_name', 'email', 'year_level', 'section', 'gender'
    )
    
    students_list = []
    for s in students:
        # Get risk level for student
        try:
            risk_assessment = RiskAssessment.objects.filter(student_id=s['id']).latest('date')
            risk_level = risk_assessment.risk_level
        except RiskAssessment.DoesNotExist:
            risk_level = None
        
        students_list.append({
            'id': s['id'],
            'name': f"{s['first_name']} {s['last_name']}",
            'email': s['email'],
            'year_level': s['year_level'],
            'section': s.get('section', ''),
            'gender': s.get('gender', ''),
            'risk_level': risk_level
        })
    
    return JsonResponse(students_list, safe=False)

@login_required
def wellness_checkin(request):
    if request.user.role != 'student':
        messages.error(request, 'Only students can submit wellness check-ins.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        stress_level = request.POST.get('stress_level')
        motivation_level = request.POST.get('motivation_level')
        workload_level = request.POST.get('workload_level')
        sleep_quality = request.POST.get('sleep_quality')
        need_help = request.POST.get('need_help') == 'true'
        comments = request.POST.get('comments', '')
        
        checkin = WellnessCheckIn.objects.create(
            student=request.user,
            stress_level=int(stress_level),
            motivation_level=int(motivation_level),
            workload_level=int(workload_level),
            sleep_quality=int(sleep_quality),
            need_help=need_help,
            text_response=comments
        )
        
        # AI Sentiment Analysis
        if comments:
            try:
                from ml_models.gemini_client import GeminiClient
                from ml_models.models import SentimentAnalysis
                
                client = GeminiClient()
                result = client.analyze_sentiment(comments)
                
                SentimentAnalysis.objects.create(
                    wellness_checkin=checkin,
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    alert_level=result['alert_level'],
                    concerning_phrases=result.get('concerning_phrases', [])
                )
                
                # Create alert if high distress
                if result['alert_level'] in ['high', 'critical']:
                    Alert.objects.create(
                        student=request.user,
                        alert_type='emotional_distress',
                        severity='high',
                        description=f"Emotional distress detected in wellness check-in"
                    )
            except Exception as e:
                pass  # Fail silently if AI analysis fails
        
        messages.success(request, 'Wellness check-in submitted successfully! Thank you for sharing.')
        return redirect('dashboard')
    
    # Get recent check-ins
    recent_checkins = WellnessCheckIn.objects.filter(student=request.user).order_by('-date')[:5]
    
    context = {
        'recent_checkins': recent_checkins,
    }
    return render(request, 'wellness/wellness_checkin.html', context)
