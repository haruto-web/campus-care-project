from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Class, Announcement, Material, Assignment, Attendance, Submission, Grade
from .forms import ClassForm, AssignmentForm, MaterialForm
from datetime import date

@login_required
def class_detail(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check if user has access
    if request.user.role == 'student':
        if request.user not in class_obj.students.all():
            messages.error(request, 'You are not enrolled in this class.')
            return redirect('dashboard')
    elif request.user.role == 'teacher':
        if class_obj.teacher != request.user:
            messages.error(request, 'You do not teach this class.')
            return redirect('dashboard')
    
    announcements = class_obj.announcements.all()
    materials = class_obj.materials.all()
    assignments = class_obj.assignments.all().order_by('-due_date')
    
    context = {
        'class': class_obj,
        'announcements': announcements,
        'materials': materials,
        'assignments': assignments,
    }
    return render(request, 'academics/class_detail.html', context)

@login_required
def create_announcement(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Only teacher can create announcements
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Only the class teacher can post announcements.')
        return redirect('academics:class_detail', class_id=class_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        priority = request.POST.get('priority', 'normal')
        
        Announcement.objects.create(
            class_obj=class_obj,
            author=request.user,
            title=title,
            content=content,
            priority=priority
        )
        messages.success(request, 'Announcement posted successfully!')
        return redirect('academics:class_detail', class_id=class_id)
    
    return render(request, 'academics/create_announcement.html', {'class': class_obj})

@login_required
def create_class(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create classes.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.teacher = request.user
            class_obj.save()
            messages.success(request, f'Class {class_obj.code} created successfully!')
            return redirect('dashboard')
    else:
        form = ClassForm()
    
    return render(request, 'academics/create_class.html', {'form': form})

@login_required
def manage_students(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Only teacher of the class can manage students
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'You do not have permission to manage students for this class.')
        return redirect('dashboard')
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get all students
    from accounts.models import User
    all_students = User.objects.filter(role='student')
    
    if search_query:
        all_students = all_students.filter(
            first_name__icontains=search_query
        ) | all_students.filter(
            last_name__icontains=search_query
        ) | all_students.filter(
            username__icontains=search_query
        ) | all_students.filter(
            email__icontains=search_query
        )
    
    enrolled_students = class_obj.students.all()
    available_students = all_students.exclude(id__in=enrolled_students.values_list('id', flat=True))
    
    context = {
        'class': class_obj,
        'enrolled_students': enrolled_students,
        'available_students': available_students,
        'search_query': search_query,
    }
    return render(request, 'academics/manage_students.html', context)

@login_required
def add_student(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    from accounts.models import User
    student = get_object_or_404(User, id=student_id, role='student')
    class_obj.students.add(student)
    messages.success(request, f'{student.get_full_name()} added to {class_obj.code}!')
    return redirect('academics:manage_students', class_id=class_id)

@login_required
def drop_student(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    from accounts.models import User
    student = get_object_or_404(User, id=student_id)
    
    # Remove student from class
    class_obj.students.remove(student)
    
    # Delete related records (grades, attendance, submissions)
    Grade.objects.filter(student=student, class_obj=class_obj).delete()
    Attendance.objects.filter(student=student, class_obj=class_obj).delete()
    Submission.objects.filter(student=student, assignment__class_obj=class_obj).delete()
    
    messages.success(request, f'{student.get_full_name()} has been dropped from {class_obj.code}. All related records have been removed.')
    return redirect('academics:manage_students', class_id=class_id)

@login_required
def create_assignment(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.class_obj = class_obj
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('academics:class_detail', class_id=class_id)
    else:
        form = AssignmentForm()
    
    return render(request, 'academics/create_assignment.html', {'form': form, 'class': class_obj})

@login_required
def mark_attendance(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    students = class_obj.students.all()
    today = date.today()
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                Attendance.objects.update_or_create(
                    class_obj=class_obj,
                    student=student,
                    date=today,
                    defaults={'status': status}
                )
        messages.success(request, 'Attendance marked successfully!')
        return redirect('academics:class_detail', class_id=class_id)
    
    # Get today's attendance
    attendance_records = {}
    for student in students:
        try:
            record = Attendance.objects.get(class_obj=class_obj, student=student, date=today)
            attendance_records[student.id] = record.status
        except Attendance.DoesNotExist:
            attendance_records[student.id] = None
    
    context = {
        'class': class_obj,
        'students': students,
        'attendance_records': attendance_records,
        'today': today,
    }
    return render(request, 'academics/mark_attendance.html', context)

@login_required
def view_submissions(request, class_id, assignment_id):
    class_obj = get_object_or_404(Class, id=class_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, class_obj=class_obj)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    submissions = assignment.submissions.all()
    students_submitted = [sub.student.id for sub in submissions]
    students_not_submitted = class_obj.students.exclude(id__in=students_submitted)
    
    context = {
        'class': class_obj,
        'assignment': assignment,
        'submissions': submissions,
        'students_not_submitted': students_not_submitted,
    }
    return render(request, 'academics/view_submissions.html', context)

@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.user.role != 'teacher' or submission.assignment.class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback', '')
        
        submission.score = int(score) if score else None
        submission.feedback = feedback
        from django.utils import timezone
        submission.graded_at = timezone.now()
        submission.save()
        
        messages.success(request, f'Graded {submission.student.get_full_name()}\'s submission!')
        return redirect('academics:view_submissions', 
                       class_id=submission.assignment.class_obj.id, 
                       assignment_id=submission.assignment.id)
    
    context = {
        'submission': submission,
    }
    return render(request, 'academics/grade_submission.html', context)

@login_required
def upload_material(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user.role != 'teacher' or class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.class_obj = class_obj
            material.uploaded_by = request.user
            material.save()
            messages.success(request, f'Material "{material.title}" uploaded successfully!')
            return redirect('academics:class_detail', class_id=class_id)
    else:
        form = MaterialForm()
    
    return render(request, 'academics/upload_material.html', {'form': form, 'class': class_obj})

@login_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.user.role != 'teacher' or material.class_obj.teacher != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    class_id = material.class_obj.id
    material.delete()
    messages.success(request, 'Material deleted successfully!')
    return redirect('academics:class_detail', class_id=class_id)

@login_required
def my_classes(request):
    if request.user.role == 'teacher':
        classes = Class.objects.filter(teacher=request.user)
        
        # Apply filters for teachers
        year_level_filter = request.GET.get('year_level_filter', '')
        section_filter = request.GET.get('section_filter', '')
        
        if year_level_filter:
            # Filter classes that have at least one student with the specified year level
            classes = classes.filter(students__year_level=year_level_filter).distinct()
        
        if section_filter:
            # Filter by section (assuming section is part of class name or code)
            classes = classes.filter(Q(name__icontains=section_filter) | Q(code__icontains=section_filter))
        
        context = {
            'classes': classes,
            'year_level_filter': year_level_filter,
            'section_filter': section_filter,
        }
    elif request.user.role == 'student':
        classes = request.user.enrolled_classes.all()
        context = {
            'classes': classes,
        }
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    return render(request, 'academics/my_classes.html', context)
