from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from .models import Class, Announcement, Material, Assignment, Attendance, Submission, Grade
from .forms import ClassForm, AssignmentForm, MaterialForm
from datetime import date, datetime, timedelta
import json

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
    
    # For students, check submission status for each assignment
    if request.user.role == 'student':
        for assignment in assignments:
            assignment.has_submission = Submission.objects.filter(
                assignment=assignment,
                student=request.user
            ).exists()
    
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
    
    # Get search query and year level filter
    search_query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')
    
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
    
    if year_level_filter:
        all_students = all_students.filter(year_level=year_level_filter)
    
    enrolled_students = class_obj.students.all()
    available_students = all_students.exclude(id__in=enrolled_students.values_list('id', flat=True))
    
    context = {
        'class': class_obj,
        'enrolled_students': enrolled_students,
        'available_students': available_students,
        'search_query': search_query,
        'year_level_filter': year_level_filter,
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
    
    # Get status filter
    status_filter = request.GET.get('status', '')
    
    # Get all submissions
    submissions = assignment.submissions.all()
    
    # Apply status filter
    if status_filter == 'graded':
        submissions = submissions.exclude(score__isnull=True)
    elif status_filter == 'pending':
        submissions = submissions.filter(score__isnull=True)
    
    students_submitted = [sub.student.id for sub in assignment.submissions.all()]
    students_not_submitted = class_obj.students.exclude(id__in=students_submitted)
    
    context = {
        'class': class_obj,
        'assignment': assignment,
        'submissions': submissions,
        'students_not_submitted': students_not_submitted,
        'status_filter': status_filter,
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
        
        # Notify student about grading
        student = submission.student
        assignment = submission.assignment
        class_obj = assignment.class_obj
        
        # Store notification message for student
        notification_msg = f'Your assignment "{assignment.title}" for {class_obj.code} - {class_obj.name} has been graded. Score: {submission.score}/{assignment.total_points}'
        
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

# Student-specific views

@login_required
def student_announcements(request):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    my_classes = request.user.enrolled_classes.all()
    announcements = Announcement.objects.filter(
        Q(class_obj__in=my_classes) | Q(class_obj__isnull=True)
    ).order_by('-created_at')
    
    # Apply filters
    priority_filter = request.GET.get('priority_filter', '')
    class_filter = request.GET.get('class_filter', '')
    date_filter = request.GET.get('date_filter', '')
    
    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)
    
    if class_filter:
        if class_filter == 'school':
            announcements = announcements.filter(class_obj__isnull=True)
        else:
            announcements = announcements.filter(class_obj_id=class_filter)
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            announcements = announcements.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            announcements = announcements.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            announcements = announcements.filter(created_at__date__gte=month_ago)
    
    # Annotate with is_read status
    announcements_list = []
    for announcement in announcements:
        announcement.is_read = announcement.read_by.filter(id=request.user.id).exists()
        announcements_list.append(announcement)
    
    context = {
        'announcements': announcements_list,
        'my_classes': my_classes,
        'priority_filter': priority_filter,
        'class_filter': class_filter,
        'date_filter': date_filter,
    }
    return render(request, 'academics/student_announcements.html', context)

@login_required
def student_materials(request):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    my_classes = request.user.enrolled_classes.all()
    materials = Material.objects.filter(class_obj__in=my_classes).order_by('-uploaded_at')
    
    # Apply filters
    class_filter = request.GET.get('class_filter', '')
    date_filter = request.GET.get('date_filter', '')
    
    if class_filter:
        materials = materials.filter(class_obj_id=class_filter)
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            materials = materials.filter(uploaded_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            materials = materials.filter(uploaded_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            materials = materials.filter(uploaded_at__date__gte=month_ago)
    
    context = {
        'materials': materials,
        'my_classes': my_classes,
        'class_filter': class_filter,
        'date_filter': date_filter,
    }
    return render(request, 'academics/student_materials.html', context)

@login_required
def student_assignments(request):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    my_classes = request.user.enrolled_classes.all()
    all_assignments = Assignment.objects.filter(class_obj__in=my_classes)
    
    now = timezone.now()
    upcoming_assignments = []
    overdue_assignments = []
    completed_assignments = []
    
    for assignment in all_assignments:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        assignment.submission = submission
        assignment.is_overdue = assignment.due_date < now
        
        if submission:
            completed_assignments.append(assignment)
        elif assignment.is_overdue:
            overdue_assignments.append(assignment)
        else:
            upcoming_assignments.append(assignment)
    
    context = {
        'upcoming_assignments': upcoming_assignments,
        'overdue_assignments': overdue_assignments,
        'completed_assignments': completed_assignments,
        'upcoming_count': len(upcoming_assignments),
        'overdue_count': len(overdue_assignments),
        'completed_count': len(completed_assignments),
    }
    return render(request, 'academics/student_assignments.html', context)

@login_required
def submit_assignment(request, assignment_id):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if student is enrolled in the class
    if request.user not in assignment.class_obj.students.all():
        messages.error(request, 'You are not enrolled in this class.')
        return redirect('academics:student_assignments')
    
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    assignment.is_overdue = assignment.due_date < timezone.now()
    
    if request.method == 'POST':
        file = request.FILES.get('file')
        comments = request.POST.get('comments', '')
        
        if file:
            if existing_submission:
                existing_submission.file = file
                existing_submission.submitted_at = timezone.now()
                existing_submission.save()
                messages.success(request, 'Assignment resubmitted successfully!')
            else:
                Submission.objects.create(
                    assignment=assignment,
                    student=request.user,
                    file=file
                )
                # Send notification to teacher
                year_level = request.user.year_level if request.user.year_level else 'N/A'
                messages.success(
                    request, 
                    f'Assignment submitted successfully! Your teacher has been notified.'
                )
                # Add notification for teacher
                from django.contrib import messages as django_messages
                teacher = assignment.class_obj.teacher
                notification_msg = f'New submission: {request.user.get_full_name()} (Grade {year_level}) submitted "{assignment.title}" for {assignment.class_obj.code} - {assignment.class_obj.name}'
                # Store in session for teacher
                from django.contrib.sessions.models import Session
                request.session[f'teacher_notification_{teacher.id}'] = notification_msg
                
            return redirect('academics:student_assignments')
        else:
            messages.error(request, 'Please upload a file.')
    
    context = {
        'assignment': assignment,
        'existing_submission': existing_submission,
    }
    return render(request, 'academics/submit_assignment.html', context)

@login_required
def student_grades(request):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    my_classes = request.user.enrolled_classes.all()
    class_filter = request.GET.get('class_filter', '')
    
    if class_filter:
        my_classes = my_classes.filter(id=class_filter)
    
    grades_by_class = []
    total_score = 0
    total_points = 0
    
    for class_obj in my_classes:
        assignments = Assignment.objects.filter(class_obj=class_obj)
        grades = []
        class_score = 0
        class_points = 0
        
        for assignment in assignments:
            submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
            if submission and submission.score is not None:
                percentage = (submission.score / assignment.total_points) * 100 if assignment.total_points > 0 else 0
                grades.append({
                    'assignment': assignment,
                    'submission': submission,
                    'score': submission.score,
                    'percentage': percentage,
                    'feedback': submission.feedback,
                })
                class_score += submission.score
                class_points += assignment.total_points
                total_score += submission.score
                total_points += assignment.total_points
            elif submission:
                grades.append({
                    'assignment': assignment,
                    'submission': submission,
                    'score': None,
                    'percentage': None,
                    'feedback': None,
                })
        
        class_average = (class_score / class_points * 100) if class_points > 0 else None
        
        if grades:
            grades_by_class.append({
                'class': class_obj,
                'grades': grades,
                'average': class_average,
            })
    
    gpa = (total_score / total_points * 4.0) if total_points > 0 else None
    
    context = {
        'grades_by_class': grades_by_class,
        'my_classes': request.user.enrolled_classes.all(),
        'class_filter': class_filter,
        'gpa': round(gpa, 2) if gpa else None,
    }
    return render(request, 'academics/student_grades.html', context)

@login_required
def student_attendance(request):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    my_classes = request.user.enrolled_classes.all()
    class_filter = request.GET.get('class_filter', '')
    month_filter = request.GET.get('month_filter', '')
    
    if class_filter:
        my_classes = my_classes.filter(id=class_filter)
    
    attendance_records = Attendance.objects.filter(student=request.user)
    
    if month_filter:
        today = timezone.now().date()
        if month_filter == 'current':
            attendance_records = attendance_records.filter(date__month=today.month, date__year=today.year)
        elif month_filter == 'last':
            last_month = today.replace(day=1) - timedelta(days=1)
            attendance_records = attendance_records.filter(date__month=last_month.month, date__year=last_month.year)
    
    # Overall stats
    present_count = attendance_records.filter(status='present').count()
    late_count = attendance_records.filter(status='late').count()
    absent_count = attendance_records.filter(status='absent').count()
    total_count = attendance_records.count()
    overall_rate = (present_count / total_count * 100) if total_count > 0 else 0
    
    # By class
    attendance_by_class = []
    for class_obj in my_classes:
        class_records = attendance_records.filter(class_obj=class_obj).order_by('-date')
        class_present = class_records.filter(status='present').count()
        class_late = class_records.filter(status='late').count()
        class_absent = class_records.filter(status='absent').count()
        class_total = class_records.count()
        class_rate = (class_present / class_total * 100) if class_total > 0 else 0
        
        if class_total > 0:
            attendance_by_class.append({
                'class': class_obj,
                'records': class_records,
                'present': class_present,
                'late': class_late,
                'absent': class_absent,
                'rate': round(class_rate, 1),
            })
    
    context = {
        'attendance_by_class': attendance_by_class,
        'my_classes': request.user.enrolled_classes.all(),
        'class_filter': class_filter,
        'month_filter': month_filter,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'total_count': total_count,
        'overall_rate': round(overall_rate, 1),
    }
    return render(request, 'academics/student_attendance.html', context)
