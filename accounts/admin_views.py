from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from accounts.models import User
from academics.models import Class
from academics.forms import ClassForm

@login_required
def admin_create_user(request):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        section = request.POST.get('section', '')
        year_level = request.POST.get('year_level', '')
        
        if role not in ['teacher', 'counselor']:
            messages.error(request, 'Invalid role selected.')
            return render(request, 'accounts/admin_create_user.html')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/admin_create_user.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/admin_create_user.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/admin_create_user.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            profile_completed=True
        )
        
        if role == 'teacher':
            subjects_input = request.POST.get('subject', '')
            sections_input = request.POST.get('section', '')
            year_level = request.POST.get('year_level', '')
            
            # Save to user profile
            if subjects_input:
                user.subject = subjects_input
            if sections_input:
                user.section = sections_input
            if year_level:
                user.year_level = year_level
            user.save()
            
            # Auto-create classes for each subject-section combination
            if subjects_input and sections_input and year_level:
                # Parse comma-separated values
                subjects = [s.strip() for s in subjects_input.split(',') if s.strip()]
                sections = [s.strip() for s in sections_input.split(',') if s.strip()]
                
                classes_created = 0
                for subject in subjects:
                    for section in sections:
                        class_code = f'G{year_level}-{section}-{subject[:3].upper()}'
                        
                        # Check if class already exists
                        if not Class.objects.filter(code=class_code).exists():
                            Class.objects.create(
                                name=subject,
                                code=class_code,
                                section=section,
                                year_level=year_level,
                                teacher=user,
                                semester='Current',
                            )
                            classes_created += 1
                
                if classes_created > 0:
                    messages.success(request, f'{role.capitalize()} account created successfully for {user.get_full_name()}! {classes_created} class(es) auto-created.')
                else:
                    messages.success(request, f'{role.capitalize()} account created successfully for {user.get_full_name()}!')
                return redirect('dashboard')
        
        messages.success(request, f'{role.capitalize()} account created successfully for {user.get_full_name()}!')
        return redirect('dashboard')
    
    return render(request, 'accounts/admin_create_user.html')

@login_required
def admin_manage_users(request):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    # Get filter parameters
    role_filter = request.GET.get('role', 'all')
    search_query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')
    section_filter = request.GET.get('section', '')
    
    # Start with all users
    users = User.objects.all()
    
    # Apply role filter
    if role_filter != 'all':
        users = users.filter(role=role_filter)
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    # Apply year level filter
    if year_level_filter:
        users = users.filter(year_level=year_level_filter)
    
    # Apply section filter
    if section_filter:
        users = users.filter(section__icontains=section_filter)
    
    users = users.order_by('role', 'last_name', 'first_name')
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
        'year_level_filter': year_level_filter,
        'section_filter': section_filter,
        'total_count': User.objects.count(),
        'student_count': User.objects.filter(role='student').count(),
        'teacher_count': User.objects.filter(role='teacher').count(),
        'counselor_count': User.objects.filter(role='counselor').count(),
    }
    return render(request, 'admin/manage_users.html', context)

@login_required
def admin_delete_user(request, user_id):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting admin accounts
    if user.role == 'admin':
        messages.error(request, 'Cannot delete admin accounts.')
        return redirect('admin_teachers_list')
    
    user_name = user.get_full_name()
    user_role = user.role
    user.delete()
    
    messages.success(request, f'{user_role.capitalize()} {user_name} has been removed successfully.')
    
    if user_role == 'teacher':
        return redirect('admin_teachers_list')
    else:
        return redirect('dashboard')

@login_required
def admin_teachers_list(request):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    teachers = User.objects.filter(role='teacher').annotate(
        classes_count=Count('classes_taught')
    ).order_by('last_name', 'first_name')
    
    context = {
        'teachers': teachers,
    }
    return render(request, 'admin/teachers_list.html', context)

@login_required
def admin_teacher_dashboard(request, teacher_id):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    
    # Get teacher's classes
    classes = Class.objects.filter(teacher=teacher)
    
    # Get all students in teacher's classes
    students = set()
    for cls in classes:
        students.update(cls.students.all())
    
    # Get at-risk students
    from wellness.models import RiskAssessment
    at_risk_students = []
    for student in students:
        latest_assessment = RiskAssessment.objects.filter(student=student).order_by('-date').first()
        if latest_assessment and latest_assessment.risk_level == 'high':
            at_risk_students.append(student)
    
    # Count pending grades
    from academics.models import Submission
    pending_grades = Submission.objects.filter(
        assignment__class_obj__in=classes,
        score__isnull=True
    ).count()
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'at_risk_students': at_risk_students,
        'total_students': len(students),
        'pending_grades': pending_grades,
        'at_risk_count': len(at_risk_students),
    }
    return render(request, 'admin/teacher_dashboard_view.html', context)

@login_required
def admin_create_class(request):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClassForm(request.POST)
        teacher_id = request.POST.get('teacher')
        
        if form.is_valid() and teacher_id:
            teacher = get_object_or_404(User, id=teacher_id, role='teacher')
            class_obj = form.save(commit=False)
            class_obj.teacher = teacher
            class_obj.save()
            messages.success(request, f'Class {class_obj.code} created successfully for {teacher.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please select a teacher.')
    else:
        form = ClassForm()
    
    teachers = User.objects.filter(role='teacher').order_by('last_name', 'first_name')
    
    context = {
        'form': form,
        'teachers': teachers,
    }
    return render(request, 'admin/create_class.html', context)

@login_required
def admin_enroll_student(request):
    if request.user.role.lower() != 'admin':
        messages.error(request, 'Permission denied. Admin access required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        class_id = request.POST.get('class')
        
        if student_id and class_id:
            student = get_object_or_404(User, id=student_id, role='student')
            class_obj = get_object_or_404(Class, id=class_id)
            
            if student in class_obj.students.all():
                messages.warning(request, f'{student.get_full_name()} is already enrolled in {class_obj.code}.')
            else:
                class_obj.students.add(student)
                messages.success(request, f'{student.get_full_name()} enrolled in {class_obj.code} successfully!')
            return redirect('admin_enroll_student')
        else:
            messages.error(request, 'Please select both student and class.')
    
    students = User.objects.filter(role='student').order_by('last_name', 'first_name')
    classes = Class.objects.all().select_related('teacher').order_by('code')
    
    # Get recent enrollments
    recent_enrollments = []
    for cls in classes[:5]:
        for student in cls.students.all()[:3]:
            recent_enrollments.append({
                'student': student,
                'class': cls
            })
    
    context = {
        'students': students,
        'classes': classes,
        'recent_enrollments': recent_enrollments[:10],
    }
    return render(request, 'admin/enroll_student.html', context)
