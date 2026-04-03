from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.dateparse import parse_datetime
from django.middleware.csrf import get_token
from .models import Class, Announcement, Material, Assignment, Attendance, Submission, Grade
from .forms import ClassForm, AssignmentForm, MaterialForm
from campus_care.validators import validate_submission_upload, validate_document_upload
from accounts.decorators import deny_access, teacher_owns_class, teacher_owns_submission
from accounts.utils import log_action, hit_rate_limit
from datetime import date, datetime, timedelta
from urllib.parse import urlencode
import calendar
import csv
import io
import json
import os
import secrets


def _teacher_class_or_redirect(request, class_obj, redirect_to='dashboard', message='Permission denied.'):
    if not teacher_owns_class(request.user, class_obj):
        return deny_access(request, redirect_to=redirect_to, message=message)
    return None


def _teacher_submission_or_redirect(request, submission, redirect_to='dashboard', message='Permission denied.'):
    if not teacher_owns_submission(request.user, submission):
        return deny_access(request, redirect_to=redirect_to, message=message)
    return None


UNDO_GRACE_SECONDS = 30


def _undo_key(token):
    return f'academics:undo:{token}'


def _stash_undo_payload(payload, grace_seconds=UNDO_GRACE_SECONDS):
    token = secrets.token_urlsafe(24)
    cache.set(_undo_key(token), payload, grace_seconds)
    return token


def _pop_undo_payload(token):
    key = _undo_key(token)
    payload = cache.get(key)
    cache.delete(key)
    return payload


def _parse_dt(value):
    if not value:
        return None
    dt = parse_datetime(value)
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _undo_inline_form(request, action_url, button_label='Undo'):
    csrf_token = get_token(request)
    return format_html(
        '<form method="post" action="{}" class="inline-block ml-2">'
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
        '<button type="submit" class="underline font-semibold">{}</button>'
        '</form>',
        action_url,
        csrf_token,
        button_label,
    )


def _first_schedule_overlap_error(blocks):
    for i in range(len(blocks)):
        first = blocks[i]
        first_days = set(first.get('days') or [])
        first_start = first.get('start_time', '')
        first_end = first.get('end_time', '')
        for j in range(i + 1, len(blocks)):
            second = blocks[j]
            second_days = set(second.get('days') or [])
            second_start = second.get('start_time', '')
            second_end = second.get('end_time', '')

            if not (first_days & second_days):
                continue

            if first_start < second_end and first_end > second_start:
                shared_days = sorted(first_days & second_days)
                shared_days_text = ', '.join(shared_days)
                return (
                    f'Conflict warning: Schedule {i + 1} overlaps with Schedule {j + 1} '
                    f'on {shared_days_text}. Please adjust the times.'
                )
    return None


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
    if not teacher_owns_class(request.user, class_obj):
        messages.error(request, 'Only the class teacher can post announcements.')
        return redirect('academics:class_detail', class_id=class_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        priority = request.POST.get('priority', 'normal')
        if priority not in dict(Announcement.PRIORITY_CHOICES):
            messages.error(request, 'Invalid announcement priority.')
            return render(request, 'academics/create_announcement.html', {'class': class_obj})
        
        announcement = Announcement.objects.create(
            class_obj=class_obj,
            author=request.user,
            title=title,
            content=content,
            priority=priority
        )
        log_action(request, 'USER_UPDATED', 'Announcement', announcement.id, announcement.title)
        messages.success(request, 'Announcement posted successfully!')
        return redirect('academics:class_detail', class_id=class_id)
    
    return render(request, 'academics/create_announcement.html', {'class': class_obj})

@login_required
def create_class(request):
    messages.error(request, 'Class creation is available through the admin only.')
    return redirect('academics:my_classes')

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
    
    # Filter by class section and year level if class has them
    if class_obj.section and class_obj.year_level:
        # Only show students from the same section AND year level
        all_students = all_students.filter(
            section__iexact=class_obj.section,
            year_level=class_obj.year_level
        )
    
    if search_query:
        all_students = all_students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
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
@require_POST
def add_student(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied
    
    from accounts.models import User
    student = get_object_or_404(User, id=student_id, role='student')
    class_obj.students.add(student)
    log_action(request, 'STUDENT_ENROLLED', 'Class', class_obj.id, class_obj.code, extra_data={'student_id': student.id})
    messages.success(request, f'{student.get_full_name()} added to {class_obj.code}!')
    
    # Preserve known filters and keep redirects internal only.
    search_query = request.GET.get('search', '')
    year_level = request.GET.get('year_level', '')
    redirect_url = reverse('academics:manage_students', kwargs={'class_id': class_id})
    query_params = {}
    if search_query:
        query_params['search'] = search_query
    if year_level:
        query_params['year_level'] = year_level
    if query_params:
        redirect_url = f'{redirect_url}?{urlencode(query_params)}'

    return redirect(redirect_url)

@login_required
@require_POST
def bulk_add_students(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied
    from accounts.models import User
    student_ids = request.POST.getlist('students')
    added = []
    added_ids = []
    for sid in student_ids:
        student = get_object_or_404(User, id=sid, role='student')
        if student not in class_obj.students.all():
            class_obj.students.add(student)
            added.append(student.get_full_name())
            added_ids.append(student.id)
    if added:
        log_action(request, 'STUDENT_ENROLLED', 'Class', class_obj.id, class_obj.code, extra_data={'student_ids': added_ids})
        messages.success(request, f'Added: {", ".join(added)}')
    return redirect('academics:manage_students', class_id=class_id)

@login_required
@require_POST
def drop_student(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied
    
    from accounts.models import User
    student = get_object_or_404(User, id=student_id, role='student')
    if not class_obj.students.filter(id=student.id).exists():
        messages.error(request, 'Student is not enrolled in this class.')
        return redirect('academics:manage_students', class_id=class_id)

    grades_payload = [
        {
            'assignment_id': grade.assignment_id,
            'score': str(grade.score),
            'max_score': str(grade.max_score),
            'date': grade.date.isoformat() if grade.date else '',
        }
        for grade in Grade.objects.filter(student=student, class_obj=class_obj)
    ]
    attendance_payload = [
        {
            'date': record.date.isoformat(),
            'status': record.status,
            'notes': record.notes,
        }
        for record in Attendance.objects.filter(student=student, class_obj=class_obj)
    ]
    submissions_payload = [
        {
            'assignment_id': submission.assignment_id,
            'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else '',
            'text_content': submission.text_content,
            'file': submission.file.name if submission.file else '',
            'score': submission.score,
            'feedback': submission.feedback,
            'graded_at': submission.graded_at.isoformat() if submission.graded_at else '',
        }
        for submission in Submission.objects.filter(student=student, assignment__class_obj=class_obj)
    ]

    token = _stash_undo_payload({
        'kind': 'undo_drop_student',
        'class_id': class_obj.id,
        'student_id': student.id,
        'grades': grades_payload,
        'attendance': attendance_payload,
        'submissions': submissions_payload,
    })

    class_obj.students.remove(student)
    Grade.objects.filter(student=student, class_obj=class_obj).delete()
    Attendance.objects.filter(student=student, class_obj=class_obj).delete()
    Submission.objects.filter(student=student, assignment__class_obj=class_obj).delete()

    log_action(request, 'STUDENT_REMOVED_FROM_CLASS', 'Class', class_obj.id, class_obj.code, extra_data={'student_id': student.id})
    messages.success(
        request,
        format_html(
            '{} has been dropped from {}. All related records were removed. {} ({}s)',
            student.get_full_name(),
            class_obj.code,
            _undo_inline_form(request, reverse('academics:undo_drop_student', args=[token])),
            UNDO_GRACE_SECONDS,
        )
    )
    return redirect('academics:manage_students', class_id=class_id)


@login_required
@require_POST
def undo_drop_student(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('kind') != 'undo_drop_student':
        messages.error(request, 'Undo link expired or is invalid.')
        return redirect('dashboard')

    class_obj = get_object_or_404(Class, id=payload['class_id'])
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied

    from accounts.models import User
    student = get_object_or_404(User, id=payload['student_id'], role='student')

    class_obj.students.add(student)

    for item in payload.get('grades', []):
        grade = Grade.objects.create(
            student=student,
            class_obj=class_obj,
            assignment_id=item['assignment_id'],
            score=item['score'],
            max_score=item['max_score'],
        )
        if item.get('date'):
            Grade.objects.filter(pk=grade.pk).update(date=item['date'])

    for item in payload.get('attendance', []):
        Attendance.objects.create(
            class_obj=class_obj,
            student=student,
            date=item['date'],
            status=item['status'],
            notes=item['notes'],
        )

    for item in payload.get('submissions', []):
        submission = Submission.objects.create(
            assignment_id=item['assignment_id'],
            student=student,
            text_content=item['text_content'],
            file=item['file'],
            score=item['score'],
            feedback=item['feedback'],
            graded_at=_parse_dt(item['graded_at']) if item.get('graded_at') else None,
        )
        if item.get('submitted_at'):
            Submission.objects.filter(pk=submission.pk).update(submitted_at=_parse_dt(item['submitted_at']))

    log_action(request, 'STUDENT_RESTORED_TO_CLASS', 'Class', class_obj.id, class_obj.code, extra_data={'student_id': student.id, 'undo_drop': True})
    messages.success(request, f'{student.get_full_name()} has been restored to {class_obj.code}.')
    return redirect('academics:manage_students', class_id=class_obj.id)

@login_required
def create_assignment(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied
    
    if request.method == 'POST':
        if hit_rate_limit(request, f'academics_create_assignment_{class_id}', limit=15, window_seconds=600):
            messages.error(request, 'Too many assignment creation attempts. Please wait before trying again.')
            return redirect('academics:class_detail', class_id=class_id)
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.class_obj = class_obj
            if assignment.total_points < 1 or assignment.total_points > 100:
                messages.error(request, 'Total points must be between 1 and 100.')
                return render(request, 'academics/create_assignment.html', {'form': form, 'class': class_obj})
            if assignment.due_date <= timezone.now():
                messages.error(request, 'Due date must be in the future.')
                return render(request, 'academics/create_assignment.html', {'form': form, 'class': class_obj})
            assignment.save()
            log_action(request, 'ASSIGNMENT_CREATED', 'Assignment', assignment.id, assignment.title, extra_data={'class_id': class_obj.id})
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('academics:class_detail', class_id=class_id)
    else:
        form = AssignmentForm()
    
    return render(request, 'academics/create_assignment.html', {'form': form, 'class': class_obj})

@login_required
def mark_attendance(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied
    
    students = class_obj.students.all()
    today = date.today()
    
    if request.method == 'POST':
        allowed_statuses = {'present', 'absent', 'late'}
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                if status not in allowed_statuses:
                    messages.error(request, 'Invalid attendance status.')
                    return redirect('academics:mark_attendance', class_id=class_id)
                Attendance.objects.update_or_create(
                    class_obj=class_obj,
                    student=student,
                    date=today,
                    defaults={'status': status}
                )
        log_action(request, 'ATTENDANCE_MARKED', 'Class', class_obj.id, class_obj.code, extra_data={'date': str(today), 'student_count': students.count()})
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
    
    denied = _teacher_submission_or_redirect(request, submission)
    if denied:
        return denied
    
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback', '')
        
        if score:
            try:
                score_val = int(score)
            except (ValueError, TypeError):
                messages.error(request, 'Invalid score value.')
                return redirect('academics:grade_submission', submission_id=submission_id)
            if score_val < 0 or score_val > submission.assignment.total_points:
                messages.error(request, f'Score must be between 0 and {submission.assignment.total_points}.')
                return redirect('academics:grade_submission', submission_id=submission_id)
            submission.score = score_val
        else:
            submission.score = None
        submission.feedback = feedback
        from django.utils import timezone
        submission.graded_at = timezone.now()
        submission.save()
        log_action(
            request,
            'SUBMISSION_GRADED',
            'Submission',
            submission.id,
            submission.assignment.title,
            extra_data={'student_id': submission.student_id, 'score': submission.score},
        )
        
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
    
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied
    
    if request.method == 'POST':
        if hit_rate_limit(request, f'academics_upload_material_{class_id}', limit=15, window_seconds=600):
            messages.error(request, 'Too many material uploads. Please wait before trying again.')
            return redirect('academics:class_detail', class_id=class_id)
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            # Validate file upload
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                allowed_material_extensions = {
                    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
                    '.xls', '.xlsx', '.txt', '.zip', '.csv',
                }
                ext = os.path.splitext(uploaded_file.name)[1].lower()
                if ext not in allowed_material_extensions:
                    messages.error(request, 'Unsupported file type for class materials. Use PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, ZIP, or CSV.')
                    return render(request, 'academics/upload_material.html', {'form': form, 'class': class_obj})
                try:
                    validate_document_upload(uploaded_file)
                except ValidationError as e:
                    messages.error(request, str(e.message))
                    return render(request, 'academics/upload_material.html', {'form': form, 'class': class_obj})
            material = form.save(commit=False)
            material.class_obj = class_obj
            material.uploaded_by = request.user
            try:
                material.save()
            except Exception:
                if uploaded_file:
                    try:
                        fallback_storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
                        fallback_name = fallback_storage.save(f"materials/{uploaded_file.name}", uploaded_file)
                        material.file = fallback_name
                        material.save()
                    except Exception:
                        messages.error(request, 'Material upload failed. Please upload a supported document file and try again.')
                        return render(request, 'academics/upload_material.html', {'form': form, 'class': class_obj})
                else:
                    messages.error(request, 'Material upload failed. Please try again.')
                    return render(request, 'academics/upload_material.html', {'form': form, 'class': class_obj})
            log_action(request, 'MATERIAL_UPLOADED', 'Material', material.id, material.title, extra_data={'class_id': class_obj.id})
            messages.success(request, f'Material "{material.title}" uploaded successfully!')
            return redirect('academics:class_detail', class_id=class_id)
    else:
        form = MaterialForm()
    
    return render(request, 'academics/upload_material.html', {'form': form, 'class': class_obj})

@login_required
@require_POST
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    denied = _teacher_class_or_redirect(request, material.class_obj)
    if denied:
        return denied
    
    class_id = material.class_obj.id
    undo_token = _stash_undo_payload({
        'type': 'material_delete',
        'actor_id': request.user.id,
        'class_id': class_id,
        'material': {
            'title': material.title,
            'description': material.description,
            'file': material.file.name if material.file else '',
            'uploaded_by_id': material.uploaded_by_id,
            'uploaded_at': material.uploaded_at.isoformat() if material.uploaded_at else '',
        },
    })
    undo_url = reverse('academics:undo_material_delete', kwargs={'token': undo_token})
    log_action(
        request,
        'MATERIAL_DELETED',
        'Material',
        material.id,
        material.title,
        extra_data={'class_id': class_id, 'undo_window_seconds': UNDO_GRACE_SECONDS},
    )
    material.delete()
    messages.warning(
        request,
        format_html(
            'Material deleted. {} ({}s)',
            _undo_inline_form(request, undo_url),
            UNDO_GRACE_SECONDS,
        ),
    )
    return redirect('academics:class_detail', class_id=class_id)


@login_required
@require_POST
def undo_material_delete(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('type') != 'material_delete':
        messages.error(request, 'Undo link is no longer valid.')
        return redirect('academics:my_classes')
    if payload.get('actor_id') != request.user.id:
        messages.error(request, 'You do not have permission to undo this action.')
        return redirect('academics:my_classes')

    class_obj = get_object_or_404(Class, id=payload.get('class_id'))
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied

    data = payload.get('material', {})
    restored = Material.objects.create(
        class_obj=class_obj,
        title=data.get('title', 'Restored Material'),
        description=data.get('description', ''),
        file=data.get('file', ''),
        uploaded_by_id=data.get('uploaded_by_id') or request.user.id,
    )
    uploaded_at = _parse_dt(data.get('uploaded_at'))
    if uploaded_at:
        Material.objects.filter(id=restored.id).update(uploaded_at=uploaded_at)

    log_action(
        request,
        'MATERIAL_RESTORED',
        'Material',
        restored.id,
        restored.title,
        extra_data={'class_id': class_obj.id, 'restored_via_undo': True},
    )
    messages.success(request, 'Material restored successfully.')
    return redirect('academics:class_detail', class_id=class_obj.id)

@login_required
def my_classes(request):
    def build_schedule_calendar(class_queryset):
        ordered_days = [choice[0] for choice in Class.DAY_CHOICES]
        day_buckets = {day: [] for day in ordered_days}

        for cls in class_queryset:
            for block in Class.parse_schedule_blocks(cls.schedule):
                start_display = Class._input_to_display_time(block['start_time'])
                end_display = Class._input_to_display_time(block['end_time'])
                block_classroom = (block.get('classroom') or '').strip()
                for day in block['days']:
                    day_buckets.setdefault(day, []).append({
                        'class': cls,
                        'start_time': block['start_time'],
                        'start_display': start_display,
                        'end_display': end_display,
                        'classroom': block_classroom,
                    })

        schedule_days = []
        for day in ordered_days:
            entries = sorted(day_buckets.get(day, []), key=lambda item: item['start_time'])
            schedule_days.append({
                'day': day,
                'short_day': day[:3],
                'entries': entries,
            })
        return schedule_days

    def build_student_schedule_export_rows(class_queryset):
        day_order = {day: index for index, (day, _) in enumerate(Class.DAY_CHOICES)}
        rows = []
        for cls in class_queryset:
            for block in Class.parse_schedule_blocks(cls.schedule):
                days = block.get('days') or []
                if not days:
                    continue
                classroom = (block.get('classroom') or '').strip()
                for day in days:
                    rows.append({
                        'day': day,
                        'day_index': day_order.get(day, 99),
                        'start_time': block['start_time'],
                        'end_time': block['end_time'],
                        'start_display': Class._input_to_display_time(block['start_time']),
                        'end_display': Class._input_to_display_time(block['end_time']),
                        'subject': cls.name,
                        'code': cls.code,
                        'teacher': cls.teacher.get_full_name() if cls.teacher else '',
                        'section': cls.section or '',
                        'year_level': cls.year_level or '',
                        'classroom': classroom or (cls.room or ''),
                    })
        rows.sort(key=lambda item: (item['day_index'], item['start_time'], item['code'], item['subject']))
        return rows

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
            'schedule_calendar_days': build_schedule_calendar(classes),
        }
    elif request.user.role == 'student':
        classes = request.user.enrolled_classes.all()
        export_rows = build_student_schedule_export_rows(classes)
        context = {
            'classes': classes,
            'schedule_calendar_days': build_schedule_calendar(classes),
            'schedule_export_available': bool(export_rows),
        }
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    return render(request, 'academics/my_classes.html', context)


@login_required
def export_student_schedule(request):
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    classes = request.user.enrolled_classes.all()
    day_order = {day: index for index, (day, _) in enumerate(Class.DAY_CHOICES)}
    rows = []
    for cls in classes:
        for block in Class.parse_schedule_blocks(cls.schedule):
            days = block.get('days') or []
            if not days:
                continue
            classroom = (block.get('classroom') or '').strip()
            for day in days:
                rows.append({
                    'day': day,
                    'day_index': day_order.get(day, 99),
                    'start_time': block['start_time'],
                    'end_time': block['end_time'],
                    'start_display': Class._input_to_display_time(block['start_time']),
                    'end_display': Class._input_to_display_time(block['end_time']),
                    'subject': cls.name,
                    'code': cls.code,
                    'teacher': cls.teacher.get_full_name() if cls.teacher else '',
                    'section': cls.section or '',
                    'year_level': cls.year_level or '',
                    'classroom': classroom or (cls.room or ''),
                })
    rows.sort(key=lambda item: (item['day_index'], item['start_time'], item['code'], item['subject']))

    if not rows:
        messages.warning(request, 'No available class schedules to export.')
        return redirect('academics:my_classes')

    export_format = (request.GET.get('format') or 'csv').lower()
    now_stamp = timezone.localtime().strftime('%Y%m%d_%H%M%S')

    if export_format == 'ics':
        day_to_byday = {
            'Monday': 'MO',
            'Tuesday': 'TU',
            'Wednesday': 'WE',
            'Thursday': 'TH',
            'Friday': 'FR',
            'Saturday': 'SA',
            'Sunday': 'SU',
        }
        day_to_weekday_index = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        def next_date_for_day(day_name):
            today = timezone.localdate()
            target = day_to_weekday_index[day_name]
            delta = (target - today.weekday()) % 7
            return today + timedelta(days=delta)

        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//BrightTrack//Student Schedule//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            f'X-WR-CALNAME:BrightTrack Schedule - {request.user.get_full_name() or request.user.username}',
        ]

        generated_at_utc = timezone.now().strftime('%Y%m%dT%H%M%SZ')
        for index, row in enumerate(rows, start=1):
            base_date = next_date_for_day(row['day'])
            dt_start = f'{base_date.strftime("%Y%m%d")}T{row["start_time"].replace(":", "")}00'
            dt_end = f'{base_date.strftime("%Y%m%d")}T{row["end_time"].replace(":", "")}00'
            lines.extend([
                'BEGIN:VEVENT',
                f'UID:brighttrack-schedule-{request.user.id}-{index}-{now_stamp}@brighttrack',
                f'DTSTAMP:{generated_at_utc}',
                f'SUMMARY:{row["subject"]} ({row["code"]})',
                f'DESCRIPTION:Teacher: {row["teacher"] or "TBA"} | Section: {row["section"] or "N/A"} | Grade: {row["year_level"] or "N/A"}',
                f'LOCATION:{row["classroom"] or "TBA"}',
                f'DTSTART:{dt_start}',
                f'DTEND:{dt_end}',
                f'RRULE:FREQ=WEEKLY;BYDAY={day_to_byday[row["day"]]}',
                'END:VEVENT',
            ])
        lines.append('END:VCALENDAR')

        response = HttpResponse('\r\n'.join(lines) + '\r\n', content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="brighttrack_schedule_{now_stamp}.ics"'
        return response

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Day', 'Start Time', 'End Time', 'Subject', 'Class Code', 'Teacher', 'Section', 'Grade Level', 'Classroom'])
    for row in rows:
        writer.writerow([
            row['day'],
            row['start_display'],
            row['end_display'],
            row['subject'],
            row['code'],
            row['teacher'],
            row['section'],
            row['year_level'],
            row['classroom'],
        ])

    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="brighttrack_schedule_{now_stamp}.csv"'
    return response

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
    submitted_ids = set(
        Submission.objects.filter(
            student=request.user,
            assignment__class_obj__in=my_classes
        ).values_list('assignment_id', flat=True)
    )
    
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

    due_soon_deadline = now + timedelta(hours=24)
    due_soon_assignments = [
        assignment for assignment in upcoming_assignments
        if assignment.id not in submitted_ids and assignment.due_date <= due_soon_deadline
    ]

    # Missed work recovery plan (prioritized, student-focused)
    recovery_plan = []
    overdue_sorted = sorted(
        overdue_assignments,
        key=lambda assignment: assignment.due_date
    )
    for assignment in overdue_sorted:
        days_late = max((now - assignment.due_date).days, 1)
        recovery_plan.append({
            'assignment': assignment,
            'status': 'overdue',
            'priority_label': 'High',
            'urgency_text': f'{days_late} day{"s" if days_late != 1 else ""} overdue',
        })

    upcoming_sorted = sorted(
        [assignment for assignment in upcoming_assignments if assignment.id not in submitted_ids],
        key=lambda assignment: assignment.due_date
    )
    for assignment in upcoming_sorted[:3]:
        hours_left = max(int((assignment.due_date - now).total_seconds() // 3600), 0)
        recovery_plan.append({
            'assignment': assignment,
            'status': 'upcoming',
            'priority_label': 'Medium',
            'urgency_text': f'Due in {hours_left}h' if hours_left < 48 else f'Due on {assignment.due_date.strftime("%b %d, %I:%M %p")}',
        })

    recovery_plan = recovery_plan[:6]

    # Assignment calendar (monthly view)
    calendar_month_raw = request.GET.get('calendar_month', '')
    today = timezone.localdate()
    try:
        if calendar_month_raw:
            calendar_month_date = datetime.strptime(calendar_month_raw, '%Y-%m').date()
            calendar_month_date = calendar_month_date.replace(day=1)
        else:
            calendar_month_date = today.replace(day=1)
    except ValueError:
        calendar_month_date = today.replace(day=1)

    month_start = calendar_month_date
    _, month_last_day = calendar.monthrange(month_start.year, month_start.month)
    month_end = month_start.replace(day=month_last_day)

    month_assignments = all_assignments.filter(
        due_date__date__gte=month_start,
        due_date__date__lte=month_end,
    ).order_by('due_date')

    calendar_filter = request.GET.get('calendar_filter', 'all')
    if calendar_filter not in {'all', 'upcoming', 'overdue', 'submitted'}:
        calendar_filter = 'all'

    events_by_date = {}
    for assignment in month_assignments:
        event_date = timezone.localtime(assignment.due_date).date()
        submission = assignment.id in submitted_ids
        is_submitted = bool(submission)
        is_overdue = assignment.due_date < now and not is_submitted
        status = 'submitted' if is_submitted else ('overdue' if is_overdue else 'upcoming')
        if calendar_filter != 'all' and status != calendar_filter:
            continue
        events_by_date.setdefault(event_date, []).append({
            'assignment': assignment,
            'status': status,
            'time_label': timezone.localtime(assignment.due_date).strftime('%I:%M %p').lstrip('0'),
        })

    month_grid = []
    for week in calendar.Calendar(firstweekday=0).monthdatescalendar(month_start.year, month_start.month):
        week_cells = []
        for day in week:
            day_events = events_by_date.get(day, [])
            week_cells.append({
                'date': day,
                'in_month': day.month == month_start.month,
                'is_today': day == today,
                'events': day_events[:3],
                'extra_count': max(len(day_events) - 3, 0),
            })
        month_grid.append(week_cells)

    prev_month = (month_start.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (month_end + timedelta(days=1)).replace(day=1)
    
    context = {
        'upcoming_assignments': upcoming_assignments,
        'overdue_assignments': overdue_assignments,
        'completed_assignments': completed_assignments,
        'upcoming_count': len(upcoming_assignments),
        'overdue_count': len(overdue_assignments),
        'completed_count': len(completed_assignments),
        'due_soon_assignments': due_soon_assignments,
        'due_soon_count': len(due_soon_assignments),
        'recovery_plan': recovery_plan,
        'recovery_plan_count': len(recovery_plan),
        'assignment_calendar_filter': calendar_filter,
        'assignment_calendar_month': month_start,
        'assignment_calendar_weeks': month_grid,
        'assignment_calendar_month_param': month_start.strftime('%Y-%m'),
        'assignment_prev_calendar_month': prev_month.strftime('%Y-%m'),
        'assignment_next_calendar_month': next_month.strftime('%Y-%m'),
        'assignment_calendar_day_names': list(calendar.day_abbr),
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
    
    context = {
        'assignment': assignment,
        'existing_submission': existing_submission,
    }
    
    if request.method == 'POST':
        if hit_rate_limit(request, f'academics_submit_assignment_{assignment_id}', limit=10, window_seconds=600):
            messages.error(request, 'Too many submission attempts. Please wait before trying again.')
            return redirect('academics:submit_assignment', assignment_id=assignment_id)
        file = request.FILES.get('file')
        text_content = request.POST.get('text_content', '').strip()
        sub_type = assignment.submission_type
        
        # Validate based on submission type
        if sub_type == 'file_upload' and not file:
            messages.error(request, 'Please upload a file.')
        elif sub_type == 'text_entry' and not text_content:
            messages.error(request, 'Please enter your answer.')
        elif sub_type == 'both' and not file and not text_content:
            messages.error(request, 'Please upload a file or enter your answer.')
        else:
            # Validate file if provided
            if file:
                try:
                    validate_submission_upload(file)
                except ValidationError as e:
                    messages.error(request, str(e.message))
                    return render(request, 'academics/submit_assignment.html', context)
            if existing_submission:
                try:
                    if file:
                        existing_submission.file = file
                    if text_content:
                        existing_submission.text_content = text_content
                    existing_submission.score = None
                    existing_submission.feedback = ''
                    existing_submission.graded_at = None
                    existing_submission.save()
                except Exception:
                    messages.error(request, 'File upload failed. Please try again.')
                    return render(request, 'academics/submit_assignment.html', context)
                messages.success(request, 'Assignment resubmitted successfully!')
            else:
                try:
                    Submission.objects.create(
                        assignment=assignment,
                        student=request.user,
                        file=file if file else None,
                        text_content=text_content,
                    )
                except Exception:
                    messages.error(request, 'File upload failed. Please try again.')
                    return render(request, 'academics/submit_assignment.html', context)
                messages.success(request, 'Assignment submitted successfully!')
            return redirect('academics:student_assignments')
    
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
                    'feedback': submission.feedback,
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

@login_required
@require_POST
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    denied = _teacher_class_or_redirect(request, assignment.class_obj)
    if denied:
        return denied
    
    class_id = assignment.class_obj.id
    assignment_payload = {
        'type': 'assignment_delete',
        'actor_id': request.user.id,
        'class_id': class_id,
        'assignment': {
            'title': assignment.title,
            'description': assignment.description,
            'due_date': assignment.due_date.isoformat() if assignment.due_date else '',
            'total_points': assignment.total_points,
            'submission_type': assignment.submission_type,
        },
        'submissions': [
            {
                'student_id': sub.student_id,
                'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else '',
                'text_content': sub.text_content,
                'file': sub.file.name if sub.file else '',
                'score': sub.score,
                'feedback': sub.feedback,
                'graded_at': sub.graded_at.isoformat() if sub.graded_at else '',
            }
            for sub in assignment.submissions.all().select_related('student')
        ],
        'grades': [
            {
                'student_id': g.student_id,
                'score': str(g.score),
                'max_score': str(g.max_score),
                'date': g.date.isoformat() if g.date else '',
            }
            for g in Grade.objects.filter(assignment=assignment)
        ],
    }
    undo_token = _stash_undo_payload(assignment_payload)
    undo_url = reverse('academics:undo_assignment_delete', kwargs={'token': undo_token})
    log_action(
        request,
        'ASSIGNMENT_DELETED',
        'Assignment',
        assignment.id,
        assignment.title,
        extra_data={'class_id': class_id, 'undo_window_seconds': UNDO_GRACE_SECONDS},
    )
    assignment.delete()
    messages.warning(
        request,
        format_html(
            'Assignment "{}" deleted. {} ({}s)',
            assignment.title,
            _undo_inline_form(request, undo_url),
            UNDO_GRACE_SECONDS,
        ),
    )
    return redirect('academics:class_detail', class_id=class_id)


@login_required
@require_POST
def undo_assignment_delete(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('type') != 'assignment_delete':
        messages.error(request, 'Undo link is no longer valid.')
        return redirect('academics:my_classes')
    if payload.get('actor_id') != request.user.id:
        messages.error(request, 'You do not have permission to undo this action.')
        return redirect('academics:my_classes')

    class_obj = get_object_or_404(Class, id=payload.get('class_id'))
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied

    assignment_data = payload.get('assignment', {})
    restored_assignment = Assignment.objects.create(
        class_obj=class_obj,
        title=assignment_data.get('title', 'Restored Assignment'),
        description=assignment_data.get('description', ''),
        due_date=_parse_dt(assignment_data.get('due_date')) or timezone.now() + timedelta(days=1),
        total_points=assignment_data.get('total_points') or 100,
        submission_type=assignment_data.get('submission_type') or 'file_upload',
    )

    for sub in payload.get('submissions', []):
        student_id = sub.get('student_id')
        if not student_id:
            continue
        try:
            restored_sub = Submission.objects.create(
                assignment=restored_assignment,
                student_id=student_id,
                text_content=sub.get('text_content', ''),
                file=sub.get('file', ''),
                score=sub.get('score'),
                feedback=sub.get('feedback', ''),
                graded_at=_parse_dt(sub.get('graded_at')),
            )
            submitted_at = _parse_dt(sub.get('submitted_at'))
            if submitted_at:
                Submission.objects.filter(id=restored_sub.id).update(submitted_at=submitted_at)
        except Exception:
            continue

    for g in payload.get('grades', []):
        student_id = g.get('student_id')
        if not student_id:
            continue
        try:
            restored_grade = Grade.objects.create(
                student_id=student_id,
                class_obj=class_obj,
                assignment=restored_assignment,
                score=g.get('score') or '0',
                max_score=g.get('max_score') or '0',
            )
        except Exception:
            continue
        try:
            parsed_date = datetime.fromisoformat(g.get('date')) if g.get('date') else None
        except ValueError:
            parsed_date = None
        if parsed_date:
            Grade.objects.filter(id=restored_grade.id).update(
                date=parsed_date.date() if isinstance(parsed_date, datetime) else parsed_date
            )

    log_action(
        request,
        'ASSIGNMENT_RESTORED',
        'Assignment',
        restored_assignment.id,
        restored_assignment.title,
        extra_data={'class_id': class_obj.id, 'restored_via_undo': True},
    )
    messages.success(request, f'Assignment "{restored_assignment.title}" restored successfully.')
    return redirect('academics:class_detail', class_id=class_obj.id)

@login_required
@require_POST
def comment_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if not teacher_owns_submission(request.user, submission):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    comment = request.POST.get('comment', '').strip()
    submission.feedback = comment
    submission.save(update_fields=['feedback'])
    log_action(request, 'GRADE_CHANGED', 'Submission', submission.id, submission.assignment.title, extra_data={'comment_updated': True})
    return JsonResponse({'success': True, 'comment': comment})

@login_required
def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    denied = _teacher_class_or_redirect(request, class_obj)
    if denied:
        return denied

    schedule_blocks = Class.parse_schedule_blocks(class_obj.schedule)
    if request.method == 'POST':
        raw_schedule_blocks = request.POST.get('schedule_blocks', '[]')
        valid_days = {choice[0] for choice in Class.DAY_CHOICES}
        try:
            submitted_blocks = json.loads(raw_schedule_blocks)
        except (TypeError, ValueError):
            submitted_blocks = None

        if not isinstance(submitted_blocks, list):
            messages.error(request, 'Invalid schedule data.')
            return render(request, 'academics/edit_class.html', {
                'class': class_obj,
                'day_choices': Class.DAY_CHOICES,
                'schedule_blocks_json': raw_schedule_blocks,
            })

        normalized_blocks = []
        for block in submitted_blocks:
            if not isinstance(block, dict):
                messages.error(request, 'Invalid schedule entry.')
                return render(request, 'academics/edit_class.html', {
                    'class': class_obj,
                    'day_choices': Class.DAY_CHOICES,
                    'schedule_blocks_json': raw_schedule_blocks,
                })

            schedule_days = [day for day in (block.get('days') or []) if day]
            schedule_start_time = (block.get('start_time') or '').strip()
            schedule_end_time = (block.get('end_time') or '').strip()
            schedule_classroom = (block.get('classroom') or '').strip()

            if not any([schedule_days, schedule_start_time, schedule_end_time]):
                continue

            if not all([schedule_days, schedule_start_time, schedule_end_time]):
                messages.error(request, 'Each schedule entry must include class day(s), start time, and end time.')
                return render(request, 'academics/edit_class.html', {
                    'class': class_obj,
                    'day_choices': Class.DAY_CHOICES,
                    'schedule_blocks_json': raw_schedule_blocks,
                })

            if any(day not in valid_days for day in schedule_days):
                messages.error(request, 'Invalid class day selected.')
                return render(request, 'academics/edit_class.html', {
                    'class': class_obj,
                    'day_choices': Class.DAY_CHOICES,
                    'schedule_blocks_json': raw_schedule_blocks,
                })

            try:
                Class._input_to_display_time(schedule_start_time)
                Class._input_to_display_time(schedule_end_time)
            except ValueError:
                messages.error(request, 'Invalid schedule time selected.')
                return render(request, 'academics/edit_class.html', {
                    'class': class_obj,
                    'day_choices': Class.DAY_CHOICES,
                    'schedule_blocks_json': raw_schedule_blocks,
                })

            if schedule_start_time >= schedule_end_time:
                messages.error(request, 'Each schedule entry must end after it starts.')
                return render(request, 'academics/edit_class.html', {
                    'class': class_obj,
                    'day_choices': Class.DAY_CHOICES,
                    'schedule_blocks_json': raw_schedule_blocks,
                })

            normalized_blocks.append({
                'days': schedule_days,
                'start_time': schedule_start_time,
                'end_time': schedule_end_time,
                'classroom': schedule_classroom,
            })

        overlap_error = _first_schedule_overlap_error(normalized_blocks)
        if overlap_error:
            messages.error(request, overlap_error)
            return render(request, 'academics/edit_class.html', {
                'class': class_obj,
                'day_choices': Class.DAY_CHOICES,
                'schedule_blocks_json': raw_schedule_blocks,
            })

        class_obj.name = request.POST.get('name')
        class_obj.description = request.POST.get('description', '')
        class_obj.schedule = Class.build_schedule_blocks(normalized_blocks)
        class_obj.save()
        log_action(request, 'USER_UPDATED', 'Class', class_obj.id, class_obj.code)
        messages.success(request, 'Class updated successfully!')
        return redirect('academics:class_detail', class_id=class_id)

    return render(request, 'academics/edit_class.html', {
        'class': class_obj,
        'day_choices': Class.DAY_CHOICES,
        'schedule_blocks_json': json.dumps(schedule_blocks),
    })

@login_required
@require_POST
def update_attendance_ajax(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if not teacher_owns_class(request.user, class_obj):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    try:
        data = json.loads(request.body)
        student_id = int(data.get('student_id'))
        status = data.get('status')
    except (ValueError, TypeError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)
    if status not in ('present', 'absent', 'late'):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    from accounts.models import User
    student = get_object_or_404(User, id=student_id, role='student')
    if student not in class_obj.students.all():
        return JsonResponse({'error': 'Student not in class'}, status=400)
    Attendance.objects.update_or_create(
        class_obj=class_obj,
        student=student,
        date=date.today(),
        defaults={'status': status}
    )
    return JsonResponse({'success': True})
