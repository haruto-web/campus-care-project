from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from academics.models import Class, Assignment, Submission, Attendance, Grade
from wellness.models import WellnessCheckIn, RiskAssessment, Alert, Intervention
from .models import User

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = 'student'  # Only students can register
        phone = request.POST.get('phone', '')
        year_level = request.POST.get('year_level', '')
        gender = request.POST.get('gender', '')
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone
        )
        
        # Set year_level for students
        if year_level:
            user.year_level = year_level
        
        # Set gender
        if gender:
            user.gender = gender
        
        user.save()
        
        # Log the user in automatically
        login(request, user)
        
        # Students go to profile completion
        messages.success(request, 'Account created successfully! Please complete your profile.')
        return redirect('complete_profile')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    
    # Only students need profile completion
    if not user.profile_completed and user.role == 'student':
        return redirect('complete_profile')
    
    if user.role == 'student':
        return student_dashboard(request)
    elif user.role == 'teacher':
        return teacher_dashboard(request)
    elif user.role == 'counselor':
        return counselor_dashboard(request)
    else:
        return admin_dashboard(request)

def student_dashboard(request):
    user = request.user
    classes = user.enrolled_classes.all()
    
    # Get upcoming assignments
    assignments = Assignment.objects.filter(
        class_obj__in=classes,
        due_date__gte=datetime.now()
    ).order_by('due_date')[:5]
    
    # Get recent announcements (unread only)
    from academics.models import Announcement
    announcements = Announcement.objects.filter(
        Q(class_obj__in=classes) | Q(class_obj__isnull=True)
    ).exclude(read_by=user).order_by('-created_at')[:3]
    
    # Get recently graded assignments (last 5)
    recently_graded = Submission.objects.filter(
        student=user,
        score__isnull=False
    ).select_related('assignment', 'assignment__class_obj').order_by('-graded_at')[:5]
    
    # Get last wellness check-in
    last_checkin = WellnessCheckIn.objects.filter(student=user).order_by('-date').first()
    
    # Count missing assignments
    all_assignments = Assignment.objects.filter(class_obj__in=classes)
    submitted_ids = Submission.objects.filter(student=user).values_list('assignment_id', flat=True)
    missing_assignments = all_assignments.exclude(id__in=submitted_ids).count()
    
    context = {
        'classes': classes,
        'assignments': assignments,
        'announcements': announcements,
        'recently_graded': recently_graded,
        'last_checkin': last_checkin,
        'missing_assignments': missing_assignments,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

def teacher_dashboard(request):
    user = request.user
    classes = Class.objects.filter(teacher=user)
    
    # Get all students in teacher's classes
    students = set()
    for cls in classes:
        students.update(cls.students.all())
    
    # Get at-risk students
    at_risk_students = []
    for student in students:
        latest_assessment = RiskAssessment.objects.filter(student=student).order_by('-date').first()
        if latest_assessment and latest_assessment.risk_level == 'high':
            at_risk_students.append(student)
    
    # Count pending grades
    pending_grades = Submission.objects.filter(
        assignment__class_obj__in=classes,
        score__isnull=True
    ).count()
    
    # Get recent submissions (last 10)
    recent_submissions = Submission.objects.filter(
        assignment__class_obj__in=classes
    ).select_related('student', 'assignment', 'assignment__class_obj').order_by('-submitted_at')[:10]
    
    context = {
        'classes': classes,
        'at_risk_students': at_risk_students,
        'total_students': len(students),
        'pending_grades': pending_grades,
        'at_risk_count': len(at_risk_students),
        'recent_submissions': recent_submissions,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)

def counselor_dashboard(request):
    # Get risk assessments
    high_risk_students = RiskAssessment.objects.filter(
        risk_level='high'
    ).order_by('-risk_score')[:10]
    
    high_risk_count = RiskAssessment.objects.filter(risk_level='high').count()
    medium_risk_count = RiskAssessment.objects.filter(risk_level='medium').count()
    
    # Get alerts
    alerts = Alert.objects.filter(resolved=False).order_by('-created_at')[:10]
    unread_alerts = Alert.objects.filter(is_read=False).count()
    
    # Get upcoming interventions
    upcoming_interventions = Intervention.objects.filter(
        status='scheduled',
        scheduled_date__gte=datetime.now()
    ).order_by('scheduled_date')[:5]
    
    pending_interventions = Intervention.objects.filter(status='scheduled').count()
    
    context = {
        'high_risk_students': high_risk_students,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'alerts': alerts,
        'unread_alerts': unread_alerts,
        'upcoming_interventions': upcoming_interventions,
        'pending_interventions': pending_interventions,
    }
    return render(request, 'dashboard/counselor_dashboard.html', context)

def admin_dashboard(request):
    from django.db.models import Count
    from datetime import datetime, timedelta
    from django.core.management import call_command
    
    # Auto-calculate risk assessments if none exist or if last calculation was > 1 day ago
    latest_assessment = RiskAssessment.objects.order_by('-date').first()
    if not latest_assessment or (datetime.now().date() - latest_assessment.date).days > 0:
        try:
            call_command('calculate_risk')
        except:
            pass
    
    # User statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_counselors = User.objects.filter(role='counselor').count()
    total_admins = User.objects.filter(role='admin').count()
    
    # Class statistics
    total_classes = Class.objects.count()
    total_assignments = Assignment.objects.count()
    
    # Top classes by enrollment
    top_classes = Class.objects.annotate(student_count=Count('students')).order_by('-student_count')[:5]
    
    # Risk statistics
    high_risk_count = RiskAssessment.objects.filter(risk_level='high').values('student').distinct().count()
    medium_risk_count = RiskAssessment.objects.filter(risk_level='medium').values('student').distinct().count()
    low_risk_count = RiskAssessment.objects.filter(risk_level='low').values('student').distinct().count()
    
    # High risk students
    high_risk_students = RiskAssessment.objects.filter(risk_level='high').select_related('student').order_by('-risk_score')[:10]
    
    # Alerts and interventions
    unresolved_alerts = Alert.objects.filter(resolved=False).count()
    pending_interventions = Intervention.objects.filter(status='scheduled').count()
    recent_alerts = Alert.objects.select_related('student').order_by('-created_at')[:5]
    
    # Activity data (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    activity_labels = []
    activity_data = []
    
    for i in range(6):
        date = datetime.now() - timedelta(days=i*5)
        activity_labels.insert(0, date.strftime('%b %d'))
        count = User.objects.filter(date_joined__gte=date - timedelta(days=5), date_joined__lt=date).count()
        activity_data.insert(0, count)
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_counselors': total_counselors,
        'total_admins': total_admins,
        'total_classes': total_classes,
        'total_assignments': total_assignments,
        'top_classes': top_classes,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'high_risk_students': high_risk_students,
        'unresolved_alerts': unresolved_alerts,
        'pending_interventions': pending_interventions,
        'recent_alerts': recent_alerts,
        'activity_labels': activity_labels,
        'activity_data': activity_data,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.phone = request.POST.get('phone', '')
        
        if request.FILES.get('profile_picture'):
            request.user.profile_picture = request.FILES['profile_picture']
        
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Add context for students
    context = {}
    if request.user.role == 'student':
        # Get GPA
        latest_assessment = RiskAssessment.objects.filter(student=request.user).order_by('-date').first()
        gpa = latest_assessment.gpa if latest_assessment else None
        
        # Calculate attendance rate
        attendance_records = Attendance.objects.filter(student=request.user)
        if attendance_records.exists():
            attendance_rate = round((attendance_records.filter(status='present').count() / attendance_records.count()) * 100, 1)
        else:
            attendance_rate = None
        
        context.update({
            'gpa': gpa,
            'attendance_rate': attendance_rate,
            'enrolled_classes_count': request.user.enrolled_classes.count(),
        })
    
    return render(request, 'accounts/profile.html' if request.user.role != 'student' else 'accounts/student_profile_edit.html', context)

@login_required
def student_profile_view(request, student_id):
    student = get_object_or_404(User, id=student_id, role='student')
    
    # Check permission - only teachers, counselors, and admins can view
    if request.user.role not in ['teacher', 'counselor', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    # Get enrolled classes
    enrolled_classes = student.enrolled_classes.all()
    
    # Get risk assessment
    risk_assessment = RiskAssessment.objects.filter(student=student).order_by('-date').first()
    
    # Get AI prediction
    from ml_models.models import PredictionLog
    ai_prediction = PredictionLog.objects.filter(
        student=student,
        prediction_type='risk'
    ).first()
    
    # Calculate attendance rate
    attendance_records = Attendance.objects.filter(student=student)
    if attendance_records.exists():
        attendance_rate = round((attendance_records.filter(status='present').count() / attendance_records.count()) * 100, 1)
    else:
        attendance_rate = None
    
    # Get recent attendance (last 10)
    recent_attendance = Attendance.objects.filter(student=student).order_by('-date')[:10]
    
    # Get wellness check-ins (last 5)
    wellness_checkins = WellnessCheckIn.objects.filter(student=student).order_by('-date')[:5]
    
    # Get concerns
    from wellness.models import TeacherConcern
    concerns = TeacherConcern.objects.filter(student=student).order_by('-date_observed')[:10]
    
    # Get interventions
    interventions = Intervention.objects.filter(student=student).order_by('-scheduled_date')[:10]
    
    # Get AI intervention recommendations if student is at risk
    ai_recommendations = None
    academic_pattern = None
    if request.user.role == 'counselor' and risk_assessment and risk_assessment.risk_level in ['medium', 'high']:
        from ml_models.gemini_client import GeminiClient
        from ml_models.utils import get_student_profile_for_intervention, get_student_academic_pattern_data
        try:
            client = GeminiClient()
            profile = get_student_profile_for_intervention(student)
            result = client.recommend_intervention(profile)
            ai_recommendations = result.get('recommendations', [])
            
            # Get academic pattern analysis
            pattern_data = get_student_academic_pattern_data(student)
            if pattern_data['assignment_scores']:  # Only analyze if there's data
                pattern_result = client.analyze_academic_pattern(pattern_data)
                academic_pattern = pattern_result
        except:
            pass
    
    context = {
        'student': student,
        'enrolled_classes': enrolled_classes,
        'risk_assessment': risk_assessment,
        'ai_prediction': ai_prediction,
        'ai_recommendations': ai_recommendations,
        'academic_pattern': academic_pattern,
        'attendance_rate': attendance_rate,
        'recent_attendance': recent_attendance,
        'wellness_checkins': wellness_checkins,
        'concerns': concerns,
        'interventions': interventions,
    }
    return render(request, 'accounts/student_profile.html', context)

@login_required
def students_list_view(request):
    # Only teachers can access this
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    # Get teacher's classes
    my_classes = Class.objects.filter(teacher=request.user)
    
    # Get all students from teacher's classes
    students = set()
    for cls in my_classes:
        students.update(cls.students.all())
    
    # Apply filters
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class_filter', '')
    year_level_filter = request.GET.get('year_level_filter', '')
    
    if class_filter:
        filtered_class = Class.objects.filter(id=class_filter, teacher=request.user).first()
        if filtered_class:
            students = set(filtered_class.students.all())
    
    if year_level_filter:
        students = [s for s in students if s.year_level == year_level_filter]
    
    if search_query:
        students = [s for s in students if 
                   search_query.lower() in s.first_name.lower() or 
                   search_query.lower() in s.last_name.lower() or 
                   search_query.lower() in s.email.lower() or 
                   search_query.lower() in s.username.lower()]
    
    # Prepare student data with stats
    students_data = []
    for student in students:
        risk_assessment = RiskAssessment.objects.filter(student=student).order_by('-date').first()
        attendance_records = Attendance.objects.filter(student=student)
        
        if attendance_records.exists():
            attendance_rate = round((attendance_records.filter(status='present').count() / attendance_records.count()) * 100, 1)
        else:
            attendance_rate = None
        
        students_data.append({
            'student': student,
            'classes_count': student.enrolled_classes.count(),
            'gpa': risk_assessment.gpa if risk_assessment else None,
            'attendance_rate': attendance_rate,
            'risk_level': risk_assessment.risk_level if risk_assessment else None,
        })
    
    # Sort by risk level (high first)
    risk_order = {'high': 0, 'medium': 1, 'low': 2, None: 3}
    students_data.sort(key=lambda x: risk_order.get(x['risk_level'], 3))
    
    context = {
        'students': students_data,
        'my_classes': my_classes,
        'search_query': search_query,
        'class_filter': class_filter,
        'year_level_filter': year_level_filter,
    }
    return render(request, 'accounts/students_list.html', context)


@login_required
def complete_profile_view(request):
    if request.user.profile_completed:
        return redirect('dashboard')
    
    if request.GET.get('skip'):
        request.user.profile_completed = True
        request.user.save()
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = request.user
        user.phone = request.POST.get('phone', '')
        user.date_of_birth = request.POST.get('date_of_birth') if request.POST.get('date_of_birth') else None
        
        # Student-specific fields
        if user.role == 'student':
            user.student_number = request.POST.get('student_number', '')
            user.section = request.POST.get('section', '')
            if request.FILES.get('id_picture'):
                user.id_picture = request.FILES['id_picture']        
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        
        user.profile_completed = True
        user.save()
        
        # Auto-enroll student in ALL classes with matching section AND year_level
        if user.role == 'student' and user.section and user.year_level:
            section_classes = Class.objects.filter(
                section__iexact=user.section,
                year_level=user.year_level
            )
            for section_class in section_classes:
                section_class.students.add(user)
        
        messages.success(request, 'Profile completed successfully!')
        return redirect('dashboard')
    
    # Route to role-specific template
    if request.user.role == 'student':
        template = 'accounts/complete_profile_student.html'
    elif request.user.role == 'teacher':
        template = 'accounts/complete_profile_teacher.html'
    elif request.user.role == 'counselor':
        template = 'accounts/complete_profile_counselor.html'
    else:
        template = 'accounts/complete_profile.html'
    
    return render(request, template)
