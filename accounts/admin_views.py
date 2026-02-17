from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from accounts.models import User
from academics.models import Class
from academics.forms import ClassForm

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
