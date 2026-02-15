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
        role = request.POST.get('role')
        phone = request.POST.get('phone', '')
        
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
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
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
    
    # Get last wellness check-in
    last_checkin = WellnessCheckIn.objects.filter(student=user).order_by('-date').first()
    
    # Calculate stats
    attendance_records = Attendance.objects.filter(student=user)
    if attendance_records.exists():
        attendance_rate = (attendance_records.filter(status='present').count() / attendance_records.count()) * 100
    else:
        attendance_rate = None
    
    # Get GPA
    latest_assessment = RiskAssessment.objects.filter(student=user).order_by('-date').first()
    gpa = latest_assessment.gpa if latest_assessment else None
    
    # Missing assignments
    missing_assignments = latest_assessment.missing_assignments if latest_assessment else 0
    
    context = {
        'classes': classes,
        'assignments': assignments,
        'last_checkin': last_checkin,
        'attendance_rate': round(attendance_rate, 1) if attendance_rate else None,
        'gpa': gpa,
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
    
    context = {
        'classes': classes,
        'at_risk_students': at_risk_students,
        'total_students': len(students),
        'pending_grades': pending_grades,
        'at_risk_count': len(at_risk_students),
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
    return counselor_dashboard(request)

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
    
    return render(request, 'accounts/profile.html')

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
    
    context = {
        'student': student,
        'enrolled_classes': enrolled_classes,
        'risk_assessment': risk_assessment,
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
    
    if class_filter:
        filtered_class = Class.objects.filter(id=class_filter, teacher=request.user).first()
        if filtered_class:
            students = set(filtered_class.students.all())
    
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
    }
    return render(request, 'accounts/students_list.html', context)
