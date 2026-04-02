from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.db import transaction
from django.db.models import Count, Q
from accounts.models import User, AuditLog, ApprovedStudent, RegistrationRequest
from accounts.decorators import admin_required, superadmin_required
from academics.models import Class
from academics.forms import ClassForm
from accounts.utils import log_action, verify_audit_entry
import csv
import io
import logging
import html
import secrets

logger = logging.getLogger('brighttrack.audit')
UNDO_GRACE_SECONDS = 30


def _undo_key(token):
    return f'admin:undo:{token}'


def _stash_undo_payload(payload, grace_seconds=UNDO_GRACE_SECONDS):
    token = secrets.token_urlsafe(24)
    cache.set(_undo_key(token), payload, grace_seconds)
    return token


def _pop_undo_payload(token):
    key = _undo_key(token)
    payload = cache.get(key)
    cache.delete(key)
    return payload


def _class_redirect_target(payload):
    return redirect(payload.get('redirect_to') or 'admin_all_classes')


def _serialize_class_for_undo(cls):
    return {
        'class': {
            'name': cls.name,
            'code': cls.code,
            'description': cls.description,
            'teacher_id': cls.teacher_id,
            'semester': cls.semester,
            'schedule': cls.schedule,
            'room': cls.room,
            'section': cls.section,
            'year_level': cls.year_level,
            'created_at': cls.created_at.isoformat() if cls.created_at else '',
        },
        'student_ids': list(cls.students.values_list('id', flat=True)),
        'announcements': [
            {
                'title': item.title,
                'content': item.content,
                'priority': item.priority,
                'is_school_wide': item.is_school_wide,
                'author_id': item.author_id,
                'created_at': item.created_at.isoformat() if item.created_at else '',
                'read_by_ids': list(item.read_by.values_list('id', flat=True)),
            }
            for item in cls.announcements.all()
        ],
        'materials': [
            {
                'title': item.title,
                'description': item.description,
                'file': item.file.name if item.file else '',
                'uploaded_by_id': item.uploaded_by_id,
                'uploaded_at': item.uploaded_at.isoformat() if item.uploaded_at else '',
            }
            for item in cls.materials.all()
        ],
        'assignments': [
            {
                'old_id': item.id,
                'title': item.title,
                'description': item.description,
                'due_date': item.due_date.isoformat() if item.due_date else '',
                'total_points': item.total_points,
                'submission_type': item.submission_type,
                'created_at': item.created_at.isoformat() if item.created_at else '',
            }
            for item in cls.assignments.all()
        ],
        'submissions': [
            {
                'assignment_old_id': submission.assignment_id,
                'student_id': submission.student_id,
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else '',
                'text_content': submission.text_content,
                'file': submission.file.name if submission.file else '',
                'score': submission.score,
                'feedback': submission.feedback,
                'graded_at': submission.graded_at.isoformat() if submission.graded_at else '',
            }
            for assignment in cls.assignments.all().prefetch_related('submissions')
            for submission in assignment.submissions.all()
        ],
        'attendance': [
            {
                'student_id': item.student_id,
                'date': item.date.isoformat(),
                'status': item.status,
                'notes': item.notes,
            }
            for item in cls.attendance_records.all()
        ],
        'grades': [
            {
                'student_id': item.student_id,
                'assignment_old_id': item.assignment_id,
                'score': str(item.score),
                'max_score': str(item.max_score),
                'date': item.date.isoformat() if item.date else '',
            }
            for item in cls.grades.all()
        ],
    }


def _restore_class_from_payload(payload):
    class_data = payload['class']
    cls = Class.objects.create(
        name=class_data['name'],
        code=class_data['code'],
        description=class_data['description'],
        teacher_id=class_data['teacher_id'],
        semester=class_data['semester'],
        schedule=class_data['schedule'],
        room=class_data['room'],
        section=class_data['section'],
        year_level=class_data['year_level'],
    )

    created_at = parse_datetime(class_data.get('created_at') or '')
    if created_at:
        Class.objects.filter(pk=cls.pk).update(created_at=created_at)

    if payload.get('student_ids'):
        cls.students.set(User.objects.filter(id__in=payload['student_ids']))

    assignment_map = {}
    from academics.models import Announcement, Assignment, Attendance, Grade, Material, Submission

    for item in payload.get('assignments', []):
        assignment = Assignment.objects.create(
            class_obj=cls,
            title=item['title'],
            description=item['description'],
            due_date=parse_datetime(item['due_date']),
            total_points=item['total_points'],
            submission_type=item['submission_type'],
        )
        assignment_map[item['old_id']] = assignment.id
        created_at = parse_datetime(item.get('created_at') or '')
        if created_at:
            Assignment.objects.filter(pk=assignment.pk).update(created_at=created_at)

    for item in payload.get('announcements', []):
        author = User.objects.filter(id=item['author_id']).first()
        if not author:
            continue
        announcement = Announcement.objects.create(
            class_obj=cls,
            author=author,
            title=item['title'],
            content=item['content'],
            priority=item['priority'],
            is_school_wide=item['is_school_wide'],
        )
        created_at = parse_datetime(item.get('created_at') or '')
        if created_at:
            Announcement.objects.filter(pk=announcement.pk).update(created_at=created_at)
        if item.get('read_by_ids'):
            announcement.read_by.set(User.objects.filter(id__in=item['read_by_ids']))

    for item in payload.get('materials', []):
        uploader = User.objects.filter(id=item['uploaded_by_id']).first()
        if not uploader:
            continue
        material = Material.objects.create(
            class_obj=cls,
            title=item['title'],
            description=item['description'],
            file=item['file'],
            uploaded_by=uploader,
        )
        uploaded_at = parse_datetime(item.get('uploaded_at') or '')
        if uploaded_at:
            Material.objects.filter(pk=material.pk).update(uploaded_at=uploaded_at)

    for item in payload.get('attendance', []):
        Attendance.objects.create(
            class_obj=cls,
            student_id=item['student_id'],
            date=item['date'],
            status=item['status'],
            notes=item['notes'],
        )

    for item in payload.get('grades', []):
        grade = Grade.objects.create(
            student_id=item['student_id'],
            class_obj=cls,
            assignment_id=assignment_map.get(item['assignment_old_id']) if item['assignment_old_id'] else None,
            score=item['score'],
            max_score=item['max_score'],
        )
        if item.get('date'):
            Grade.objects.filter(pk=grade.pk).update(date=item['date'])

    for item in payload.get('submissions', []):
        assignment_id = assignment_map.get(item['assignment_old_id'])
        if not assignment_id:
            continue
        submission = Submission.objects.create(
            assignment_id=assignment_id,
            student_id=item['student_id'],
            text_content=item['text_content'],
            file=item['file'],
            score=item['score'],
            feedback=item['feedback'],
            graded_at=parse_datetime(item['graded_at']) if item.get('graded_at') else None,
        )
        submitted_at = parse_datetime(item.get('submitted_at') or '')
        if submitted_at:
            Submission.objects.filter(pk=submission.pk).update(submitted_at=submitted_at)

    return cls


def _registration_tab_redirect():
    return redirect(f"{reverse('admin_upload_students')}?tab=registrations")


def _apply_audit_log_filters(request):
    logs = AuditLog.objects.select_related('actor').all()

    action_filter = request.GET.get('action', '')
    actor_filter = request.GET.get('actor', '')
    target_filter = request.GET.get('target', '')
    ip_filter = request.GET.get('ip', '')
    integrity_filter = request.GET.get('integrity', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if actor_filter:
        logs = logs.filter(
            Q(actor__first_name__icontains=actor_filter) |
            Q(actor__last_name__icontains=actor_filter) |
            Q(actor__username__icontains=actor_filter)
        )
    if target_filter:
        target_query = (
            Q(target_label__icontains=target_filter) |
            Q(target_type__icontains=target_filter)
        )
        if target_filter.isdigit():
            target_query |= Q(target_id=int(target_filter))
        logs = logs.filter(target_query)
    if ip_filter:
        logs = logs.filter(ip_address__icontains=ip_filter)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    logs = list(logs)
    for log in logs:
        log.integrity_ok = verify_audit_entry(log)

    if integrity_filter == 'unaltered':
        logs = [log for log in logs if log.integrity_ok is True]
    elif integrity_filter == 'not_verified':
        logs = [log for log in logs if log.integrity_ok is not True]

    return logs, {
        'action_filter': action_filter,
        'actor_filter': actor_filter,
        'target_filter': target_filter,
        'ip_filter': ip_filter,
        'integrity_filter': integrity_filter,
        'date_from': date_from,
        'date_to': date_to,
    }


def _audit_log_export_rows(logs):
    rows = []
    for log in logs:
        if log.integrity_ok is True:
            integrity_label = 'Unaltered'
        else:
            integrity_label = 'Not Verified'
        actor_label = log.actor.get_full_name() if log.actor else 'System'
        rows.append([
            timezone.localtime(log.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            actor_label,
            log.get_action_display(),
            log.target_type,
            log.target_id or '',
            log.target_label,
            log.ip_address or '',
            integrity_label,
            log.extra_data,
        ])
    return rows


def _audit_log_visual_rows(logs):
    rows = []
    for log in logs:
        integrity_label = 'Unaltered' if log.integrity_ok is True else 'Not Verified'
        actor_label = log.actor.get_full_name() if log.actor else 'System'
        target_label = log.target_label or '—'
        if log.target_type:
            target_label = f'{target_label} ({log.target_type})'
        details = '—'
        if log.extra_data:
            details = str(log.extra_data)
        rows.append([
            timezone.localtime(log.timestamp).strftime('%b %d, %Y %I:%M %p'),
            actor_label,
            log.get_action_display(),
            target_label,
            log.ip_address or '—',
            integrity_label,
            details,
        ])
    return rows


def _pdf_escape(value):
    safe = ''.join(ch if ord(ch) < 128 else '?' for ch in str(value))
    return safe.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _truncate_text(value, length):
    text = str(value or '')
    return text if len(text) <= length else f'{text[:max(0, length - 3)]}...'


def _build_simple_pdf_table(headers, rows):
    page_w, page_h = 842, 595  # A4 landscape
    left_margin = 20
    top_y = page_h - 28
    row_h = 20
    col_widths = [128, 140, 105, 210, 88, 88, 43]  # fits 7 columns

    draw_rows = []
    for row in rows:
        draw_rows.append([
            _truncate_text(row[0], 20),
            _truncate_text(row[1], 24),
            _truncate_text(row[2], 18),
            _truncate_text(row[3], 38),
            _truncate_text(row[4], 16),
            _truncate_text(row[5], 14),
            _truncate_text(row[6], 8),
        ])

    lines_per_page = max(10, int((page_h - 65) / row_h) - 1)  # header + rows
    pages = []
    for idx in range(0, len(draw_rows), lines_per_page):
        pages.append(draw_rows[idx:idx + lines_per_page])
    if not pages:
        pages = [[]]

    streams = []
    for page_rows in pages:
        total_rows = 1 + len(page_rows)  # header + data
        table_h = total_rows * row_h
        y_bottom = top_y - table_h
        x = left_margin

        ops = [
            "0.95 g",
            f"{left_margin} {top_y - row_h} {sum(col_widths)} {row_h} re f",
            "0 g",
            "0.4 w",
            f"{left_margin} {y_bottom} {sum(col_widths)} {table_h} re S",
        ]

        for i in range(1, total_rows):
            y = top_y - (i * row_h)
            ops.append(f"{left_margin} {y} m {left_margin + sum(col_widths)} {y} l S")

        for w in col_widths[:-1]:
            x += w
            ops.append(f"{x} {y_bottom} m {x} {top_y} l S")

        x = left_margin + 4
        y_text = top_y - 14
        for i, header in enumerate(headers):
            ops.append(f"BT /F1 8 Tf {x} {y_text} Td ({_pdf_escape(header)}) Tj ET")
            x += col_widths[i]

        for ridx, row in enumerate(page_rows):
            x = left_margin + 4
            y_text = top_y - row_h - 14 - (ridx * row_h)
            for cidx, cell in enumerate(row):
                ops.append(f"BT /F1 8 Tf {x} {y_text} Td ({_pdf_escape(cell)}) Tj ET")
                x += col_widths[cidx]

        streams.append("\n".join(ops).encode('latin-1', errors='replace'))

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    objects = []

    # 1 Catalog, 2 Pages
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    kids = " ".join(f"{3 + i*2} 0 R" for i in range(len(streams)))
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(streams)} >>\nendobj\n".encode('latin-1'))

    # page/content objects
    for i, stream in enumerate(streams):
        page_obj_id = 3 + i * 2
        content_obj_id = page_obj_id + 1
        objects.append(
            f"{page_obj_id} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] /Resources << /Font << /F1 {3 + len(streams)*2} 0 R >> >> /Contents {content_obj_id} 0 R >>\nendobj\n".encode('latin-1')
        )
        objects.append(
            f"{content_obj_id} 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode('latin-1') +
            stream +
            b"\nendstream\nendobj\n"
        )

    font_obj_id = 3 + len(streams) * 2
    objects.append(f"{font_obj_id} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n".encode('latin-1'))

    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode('latin-1'))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode('latin-1'))
    pdf.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode('latin-1'))
    return bytes(pdf)

@login_required
@admin_required
def admin_create_user(request):
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
        log_action(request, 'USER_CREATED', 'User', user.id, user.get_full_name(), extra_data={'role': role})
        
        if role == 'teacher':
            subjects_input = request.POST.get('subject', '')
            sections_input = request.POST.get('section', '')
            year_level = request.POST.get('year_level', '')
            
            if subjects_input:
                user.subject = subjects_input
            if sections_input:
                user.section = sections_input
            if year_level:
                user.year_level = year_level
            user.save()
            
            if subjects_input and sections_input and year_level:
                subjects = [s.strip() for s in subjects_input.split(',') if s.strip()]
                sections = [s.strip() for s in sections_input.split(',') if s.strip()]
                
                classes_created = 0
                for subject in subjects:
                    for section in sections:
                        class_code = f'G{year_level}-{section}-{subject[:3].upper()}'
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
@admin_required
def admin_manage_users(request):
    role_filter = request.GET.get('role', 'all')
    search_query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')
    section_filter = request.GET.get('section', '')
    messaging_filter = request.GET.get('messaging', '')
    
    users = User.objects.all()
    
    if role_filter != 'all':
        users = users.filter(role=role_filter)
    
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    if year_level_filter:
        users = users.filter(year_level=year_level_filter)
    
    if section_filter:
        users = users.filter(section__icontains=section_filter)

    if messaging_filter == 'suspended':
        users = users.filter(messaging_suspended_until__gt=timezone.now())
    
    users = users.filter(is_active=True).order_by('role', 'last_name', 'first_name')
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
        'year_level_filter': year_level_filter,
        'section_filter': section_filter,
        'messaging_filter': messaging_filter,
        'total_count': User.objects.filter(is_active=True).count(),
        'student_count': User.objects.filter(is_active=True, role='student').count(),
        'teacher_count': User.objects.filter(is_active=True, role='teacher').count(),
        'counselor_count': User.objects.filter(is_active=True, role='counselor').count(),
        'archived_count': User.objects.filter(is_active=False).exclude(role='admin').count(),
    }
    return render(request, 'admin/manage_users.html', context)


@login_required
@admin_required
def admin_archived_users(request):
    role_filter = request.GET.get('role', 'all')
    search_query = request.GET.get('search', '')
    users = User.objects.filter(is_active=False).exclude(role='admin')

    if role_filter != 'all':
        users = users.filter(role=role_filter)

    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )

    users = users.order_by('role', 'last_name', 'first_name')
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
        'total_archived_count': User.objects.filter(is_active=False).exclude(role='admin').count(),
        'student_archived_count': User.objects.filter(is_active=False, role='student').count(),
        'teacher_archived_count': User.objects.filter(is_active=False, role='teacher').count(),
        'counselor_archived_count': User.objects.filter(is_active=False, role='counselor').count(),
    }
    return render(request, 'admin/archived_users.html', context)


@login_required
@admin_required
@require_POST
def admin_restore_archived_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_active=False)
    user.is_active = True
    user.save(update_fields=['is_active'])
    log_action(request, 'USER_RESTORED', 'User', user.id, user.get_full_name(), extra_data={'archive_restore': True})
    messages.success(request, f'{user.get_full_name()} has been restored successfully.')
    return redirect('admin_archived_users')

@login_required
@admin_required
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method != 'POST':
        target = 'admin_teachers_list' if user.role == 'teacher' else 'admin_manage_users'
        messages.warning(request, 'User removal must be submitted from the management page.')
        return redirect(target)
    
    if user.role == 'admin':
        messages.error(request, 'Cannot delete admin accounts.')
        return redirect('admin_teachers_list')
    if not user.is_active:
        messages.error(request, 'This account is already removed.')
        return redirect('admin_teachers_list' if user.role == 'teacher' else 'admin_manage_users')
    
    user_name = user.get_full_name()
    user_role = user.role
    user.is_active = False
    user.current_session_key = ''
    user.save(update_fields=['is_active', 'current_session_key'])
    token = _stash_undo_payload({
        'kind': 'undo_user_delete',
        'user_id': user.id,
        'user_role': user_role,
    })

    logger.warning(f'User {user_name} (role={user_role}, id={user_id}) deactivated by admin {request.user.username}')
    log_action(request, 'USER_DELETED', 'User', user.id, user_name, extra_data={'role': user_role, 'soft_deleted': True})
    messages.success(
        request,
        format_html(
            '{} {} has been removed. <a href="{}" class="underline font-semibold">Undo</a> ({}s)',
            user_role.capitalize(),
            user_name,
            reverse('admin_undo_delete_user', args=[token]),
            UNDO_GRACE_SECONDS,
        )
    )
    
    if user_role == 'teacher':
        return redirect('admin_teachers_list')
    else:
        return redirect('admin_manage_users')


@login_required
@admin_required
def admin_undo_delete_user(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('kind') != 'undo_user_delete':
        messages.error(request, 'Undo link expired or is invalid.')
        return redirect('admin_manage_users')

    user = get_object_or_404(User, id=payload['user_id'])
    user.is_active = True
    user.save(update_fields=['is_active'])
    log_action(request, 'USER_RESTORED', 'User', user.id, user.get_full_name(), extra_data={'undo_user_delete': True})
    messages.success(request, f'{user.get_full_name()} has been restored.')
    return redirect('admin_teachers_list' if payload.get('user_role') == 'teacher' else 'admin_manage_users')

@login_required
@admin_required
def admin_teachers_list(request):
    teachers = User.objects.filter(role='teacher', is_active=True).annotate(
        classes_count=Count('classes_taught')
    ).order_by('last_name', 'first_name')
    
    context = {
        'teachers': teachers,
    }
    return render(request, 'admin/teachers_list.html', context)

@login_required
@admin_required
def admin_teacher_dashboard(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    classes = Class.objects.filter(teacher=teacher)
    
    students = set()
    for cls in classes:
        students.update(cls.students.all())
    
    from wellness.models import RiskAssessment
    at_risk_students = []
    for student in students:
        latest_assessment = RiskAssessment.objects.filter(student=student).order_by('-date').first()
        if latest_assessment and latest_assessment.risk_level == 'high':
            at_risk_students.append(student)
    
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
@admin_required
def admin_user_profile(request, user_id):
    viewed_user = get_object_or_404(User, id=user_id)
    classes_taught = Class.objects.filter(teacher=viewed_user).order_by('code') if viewed_user.role == 'teacher' else Class.objects.none()
    enrolled_classes = viewed_user.enrolled_classes.all().order_by('code') if viewed_user.role == 'student' else Class.objects.none()

    context = {
        'viewed_user': viewed_user,
        'classes_taught': classes_taught,
        'enrolled_classes': enrolled_classes,
    }
    return render(request, 'admin/user_profile.html', context)

@login_required
@admin_required
def admin_create_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        teacher_id = request.POST.get('teacher')
        
        if form.is_valid() and teacher_id:
            teacher = get_object_or_404(User, id=teacher_id, role='teacher')
            class_obj = form.save(commit=False)
            class_obj.teacher = teacher
            class_obj.save()
            log_action(request, 'CLASS_CREATED', 'Class', class_obj.id, class_obj.code, extra_data={'teacher_id': teacher.id})
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
@admin_required
def admin_enroll_student(request):
    if request.method == 'POST':
        student_ids = request.POST.getlist('student')
        class_id = request.POST.get('class')
        
        if student_ids and class_id:
            class_obj = get_object_or_404(Class, id=class_id)
            enrolled, skipped = [], []
            for sid in student_ids:
                student = get_object_or_404(User, id=sid, role='student')
                if student in class_obj.students.all():
                    skipped.append(student.get_full_name())
                else:
                    class_obj.students.add(student)
                    enrolled.append(student.get_full_name())
            if enrolled:
                log_action(request, 'STUDENT_ENROLLED', 'Class', class_obj.id, class_obj.code, extra_data={'student_ids': student_ids})
            if enrolled:
                messages.success(request, f'Enrolled: {", ".join(enrolled)} into {class_obj.code}.')
            if skipped:
                messages.warning(request, f'Already enrolled: {", ".join(skipped)}.')
            return redirect('admin_enroll_student')
        else:
            messages.error(request, 'Please select at least one student and a class.')
    
    students = User.objects.filter(role='student').order_by('last_name', 'first_name')
    classes = Class.objects.all().select_related('teacher').order_by('code')

    sections = User.objects.filter(role='student').exclude(section='').values_list('section', flat=True).distinct().order_by('section')
    grade_levels = User.objects.filter(role='student').exclude(year_level=None).values_list('year_level', flat=True).distinct().order_by('year_level')

    section_filter = request.GET.get('section', '')
    grade_filter = request.GET.get('grade', '')
    if section_filter:
        students = students.filter(section__iexact=section_filter)
    if grade_filter:
        students = students.filter(year_level=grade_filter)
    
    recent_enrollments = []
    for cls in classes[:5]:
        for student in cls.students.all()[:3]:
            recent_enrollments.append({'student': student, 'class': cls})
    
    context = {
        'students': students,
        'classes': classes,
        'recent_enrollments': recent_enrollments[:10],
        'sections': sections,
        'grade_levels': grade_levels,
        'section_filter': section_filter,
        'grade_filter': grade_filter,
    }
    return render(request, 'admin/enroll_student.html', context)

@login_required
@superadmin_required
def admin_cleanup_users(request):
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '').strip()
        if confirmation != 'DELETE ALL USERS':
            messages.error(request, 'Please type "DELETE ALL USERS" exactly to confirm.')
            return redirect('admin_cleanup_users')

        admins_count = User.objects.filter(role='admin').count()
        deleted_count = User.objects.exclude(role='admin').delete()[0]
        
        logger.critical(f'MASS DELETION by admin {request.user.username}: {deleted_count} users deleted, {admins_count} admins kept')
        log_action(request, 'MASS_DELETE', 'User', None, 'Non-admin users', extra_data={'deleted_count': deleted_count, 'admins_kept': admins_count})
        messages.success(request, f'Cleanup complete! Deleted {deleted_count} users. {admins_count} admin accounts kept safe.')
        return redirect('dashboard')
    
    context = {
        'total_users': User.objects.count(),
        'admin_count': User.objects.filter(role='admin').count(),
        'student_count': User.objects.filter(role='student').count(),
        'teacher_count': User.objects.filter(role='teacher').count(),
        'counselor_count': User.objects.filter(role='counselor').count(),
    }
    return render(request, 'admin/cleanup_users.html', context)

@login_required
@superadmin_required
def admin_create_superuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'admin/create_superuser.html')
        
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        try:
            validate_password(password)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, 'admin/create_superuser.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='admin',
            is_staff=True,
            is_superuser=True,
            profile_completed=True
        )
        
        logger.warning(f'Superuser {username} created by admin {request.user.username}')
        log_action(request, 'USER_CREATED', 'User', user.id, user.get_full_name(), extra_data={'role': 'admin', 'is_superuser': True})
        messages.success(request, f'Superuser {username} created successfully! You can now access Django admin.')
        return redirect('dashboard')
    
    return render(request, 'admin/create_superuser.html')


@login_required
@admin_required
def admin_upload_students(request):
    if request.method == 'POST' and request.POST.get('action') == 'manual':
        sn = request.POST.get('student_number', '').strip()
        email = request.POST.get('email', '').strip().lower()
        fn = request.POST.get('first_name', '').strip()
        ln = request.POST.get('last_name', '').strip()
        yl = request.POST.get('year_level', '').strip()
        section = request.POST.get('section', '').strip()

        if not all([sn, email, fn, ln, yl]):
            messages.error(request, 'All fields except section are required.')
        elif not sn.isdigit() or len(sn) != 12:
            messages.error(request, 'Student number must be exactly 12 digits.')
        elif yl not in ('7', '8', '9', '10'):
            messages.error(request, 'Year level must be 7, 8, 9, or 10.')
        else:
            _, created = ApprovedStudent.objects.update_or_create(
                student_number=sn,
                defaults={'email': email, 'first_name': fn, 'last_name': ln, 'year_level': yl, 'section': section}
            )
            log_action(request, 'USER_UPDATED', 'ApprovedStudent', None, f'{fn} {ln}', extra_data={'created': created, 'student_number': sn})
            messages.success(request, f'Student {fn} {ln} {"added" if created else "updated"} successfully.')
        return redirect('admin_upload_students')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv') or csv_file.content_type not in ('text/csv', 'application/vnd.ms-excel', 'text/plain'):
            messages.error(request, 'Please upload a valid .csv file.')
            return redirect('admin_upload_students')

        if csv_file.size > 5 * 1024 * 1024:
            messages.error(request, 'File too large. Maximum 5MB.')
            return redirect('admin_upload_students')

        def sanitize(val):
            if val and val[0] in ('=', '+', '-', '@'):
                return "'" + val
            return val

        decoded = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))

        required_cols = {'student_number', 'email', 'first_name', 'last_name', 'year_level'}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            messages.error(request, f'CSV must have columns: {", ".join(required_cols)}')
            return redirect('admin_upload_students')

        created, updated, skipped = 0, 0, 0
        errors = []
        for i, row in enumerate(reader, start=2):
            sn = sanitize(row.get('student_number', '').strip())
            email = row.get('email', '').strip().lower()
            fn = sanitize(row.get('first_name', '').strip())
            ln = sanitize(row.get('last_name', '').strip())
            yl = row.get('year_level', '').strip()
            section = sanitize(row.get('section', '').strip())

            if not all([sn, email, fn, ln, yl]):
                errors.append(f'Row {i}: missing required field.')
                skipped += 1
                continue

            if yl not in ('7', '8', '9', '10'):
                errors.append(f'Row {i}: invalid year_level "{yl}" (must be 7-10).')
                skipped += 1
                continue

            _, was_created = ApprovedStudent.objects.update_or_create(
                student_number=sn,
                defaults={
                    'email': email,
                    'first_name': fn,
                    'last_name': ln,
                    'year_level': yl,
                    'section': section,
                }
            )
            log_action(request, 'USER_UPDATED', 'ApprovedStudent', None, f'{fn} {ln}', extra_data={'created': was_created, 'student_number': sn, 'source': 'csv'})
            if was_created:
                created += 1
            else:
                updated += 1

        msg = f'Upload complete: {created} added, {updated} updated, {skipped} skipped.'
        if errors:
            msg += ' Errors: ' + ' | '.join(errors[:5])
        messages.success(request, msg)
        return redirect('admin_upload_students')

    approved_students = ApprovedStudent.objects.all()
    pending_registrations = RegistrationRequest.objects.filter(status=RegistrationRequest.Status.PENDING).order_by('-created_at')
    paginator = Paginator(approved_students, 50)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/upload_students.html', {
        'page_obj': page,
        'pending_registrations': pending_registrations,
        'active_tab': request.GET.get('tab', 'csv'),
    })


@login_required
@admin_required
@require_POST
def admin_suspend_approved_student(request, student_id):
    from accounts.models import ApprovedStudent
    student = get_object_or_404(ApprovedStudent, id=student_id)
    previous_state = student.is_suspended
    student.is_suspended = not student.is_suspended
    student.save()
    token = _stash_undo_payload({
        'kind': 'undo_approved_student_suspend',
        'student_id': student.id,
        'previous_state': previous_state,
    })
    log_action(request, 'APPROVED_STUDENT_STATUS_CHANGED', 'ApprovedStudent', student.id, f'{student.first_name} {student.last_name}', extra_data={'is_suspended': student.is_suspended})
    action = 'suspended' if student.is_suspended else 'unsuspended'
    messages.success(
        request,
        format_html(
            '{} {} has been {}. <a href="{}" class="underline font-semibold">Undo</a> ({}s)',
            student.first_name,
            student.last_name,
            action,
            reverse('admin_undo_suspend_approved_student', args=[token]),
            UNDO_GRACE_SECONDS,
        )
    )
    return redirect('admin_upload_students')


@login_required
@admin_required
def admin_undo_suspend_approved_student(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('kind') != 'undo_approved_student_suspend':
        messages.error(request, 'Undo link expired or is invalid.')
        return redirect('admin_upload_students')

    student = get_object_or_404(ApprovedStudent, id=payload['student_id'])
    student.is_suspended = payload['previous_state']
    student.save(update_fields=['is_suspended'])
    log_action(request, 'APPROVED_STUDENT_STATUS_RESTORED', 'ApprovedStudent', student.id, f'{student.first_name} {student.last_name}', extra_data={'undo_suspend_toggle': True, 'is_suspended': student.is_suspended})
    messages.success(request, f'{student.first_name} {student.last_name} has been restored to the previous suspension state.')
    return redirect('admin_upload_students')


@login_required
@admin_required
def admin_edit_approved_student(request, student_id):
    from accounts.models import ApprovedStudent
    student = get_object_or_404(ApprovedStudent, id=student_id)
    if request.method == 'POST':
        sn = request.POST.get('student_number', '').strip()
        email = request.POST.get('email', '').strip().lower()
        fn = request.POST.get('first_name', '').strip()
        ln = request.POST.get('last_name', '').strip()
        yl = request.POST.get('year_level', '').strip()
        section = request.POST.get('section', '').strip()
        if not all([sn, email, fn, ln, yl]):
            messages.error(request, 'All fields except section are required.')
        elif not sn.isdigit() or len(sn) != 12:
            messages.error(request, 'Student number must be exactly 12 digits.')
        elif yl not in ('7', '8', '9', '10'):
            messages.error(request, 'Year level must be 7-10.')
        elif ApprovedStudent.objects.filter(student_number=sn).exclude(id=student_id).exists():
            messages.error(request, 'Another student with that number already exists.')
        else:
            student.student_number = sn
            student.email = email
            student.first_name = fn
            student.last_name = ln
            student.year_level = yl
            student.section = section
            student.save()
            log_action(request, 'USER_UPDATED', 'ApprovedStudent', student.id, f'{student.first_name} {student.last_name}')
            messages.success(request, f'Student {fn} {ln} updated successfully.')
        return redirect('admin_upload_students')
    return redirect('admin_upload_students')


@login_required
@admin_required
@require_POST
def admin_approve_registration(request, request_id):
    with transaction.atomic():
        registration = get_object_or_404(
            RegistrationRequest.objects.select_for_update(), id=request_id
        )
        if registration.status != RegistrationRequest.Status.PENDING:
            messages.error(request, 'This registration request was already processed.')
            return _registration_tab_redirect()

        if User.objects.filter(email__iexact=registration.email).exists():
            registration.status = RegistrationRequest.Status.REJECTED
            registration.approved_by = request.user
            registration.decided_at = timezone.now()
            registration.rejection_reason = 'Email already exists'
            registration.save(update_fields=['status', 'approved_by', 'decided_at', 'rejection_reason', 'updated_at'])
            messages.error(request, 'Approval blocked: email already exists in active users.')
            return _registration_tab_redirect()

        import uuid
        base = f"{registration.first_name.lower()}{registration.last_name.lower()}".replace(' ', '')
        username = f"{base}{str(uuid.uuid4())[:4]}"
        while User.objects.filter(username=username).exists():
            username = f"{base}{str(uuid.uuid4())[:4]}"

        user = User(
            username=username,
            email=registration.email,
            first_name=registration.first_name,
            last_name=registration.last_name,
            role='student',
            student_number=registration.student_number,
            year_level=registration.year_level,
            section=registration.section,
            profile_completed=False,
        )
        user.password = registration.password_hash
        user.save()

        ApprovedStudent.objects.update_or_create(
            student_number=registration.student_number,
            defaults={
                'email': registration.email,
                'first_name': registration.first_name,
                'last_name': registration.last_name,
                'year_level': registration.year_level,
                'section': registration.section,
                'is_registered': True,
                'is_suspended': False,
            }
        )

        registration.status = RegistrationRequest.Status.APPROVED
        registration.approved_by = request.user
        registration.decided_at = timezone.now()
        registration.rejection_reason = ''
        registration.save(update_fields=['status', 'approved_by', 'decided_at', 'rejection_reason', 'updated_at'])
        log_action(request, 'USER_CREATED', 'User', user.id, user.get_full_name(), extra_data={'registration_request_id': registration.id})

    from accounts.otp_utils import send_transactional_email
    send_transactional_email(
        to_email=registration.email,
        subject='BrightTrack Registration Approved',
        text_content=(
            f"Dear {registration.first_name.title()} {registration.last_name.title()},\n\n"
            "Your account registration request has been approved by the administrator.\n"
            "You can now log in to BrightTrack using your registered email and password.\n\n"
            "BrightTrack School System"
        ),
    )
    messages.success(request, f'Registration approved for {registration.first_name} {registration.last_name}.')
    return _registration_tab_redirect()


@login_required
@admin_required
@require_POST
def admin_reject_registration(request, request_id):
    registration = get_object_or_404(RegistrationRequest, id=request_id)
    if registration.status != RegistrationRequest.Status.PENDING:
        messages.error(request, 'This registration request was already processed.')
        return _registration_tab_redirect()

    reason = (request.POST.get('reason') or '').strip()
    if not reason:
        reason = 'Registration details did not pass school approval.'

    registration.status = RegistrationRequest.Status.REJECTED
    registration.approved_by = request.user
    registration.decided_at = timezone.now()
    registration.rejection_reason = reason[:255]
    registration.save(update_fields=['status', 'approved_by', 'decided_at', 'rejection_reason', 'updated_at'])
    token = _stash_undo_payload({
        'kind': 'undo_reject_registration',
        'registration_id': registration.id,
    })
    log_action(request, 'REGISTRATION_REJECTED', 'RegistrationRequest', registration.id, registration.email, extra_data={'status': registration.status})

    from accounts.otp_utils import send_transactional_email
    send_transactional_email(
        to_email=registration.email,
        subject='BrightTrack Registration Rejected',
        text_content=(
            f"Dear {registration.first_name.title()} {registration.last_name.title()},\n\n"
            "Your account registration request was not approved by the administrator.\n"
            f"Reason: {registration.rejection_reason}\n\n"
            "No account was created. You may contact your school administrator for assistance.\n\n"
            "BrightTrack School System"
        ),
    )
    messages.success(
        request,
        format_html(
            'Registration rejected for {} {}. <a href="{}" class="underline font-semibold">Undo</a> ({}s)',
            registration.first_name,
            registration.last_name,
            reverse('admin_undo_reject_registration', args=[token]),
            UNDO_GRACE_SECONDS,
        )
    )
    return _registration_tab_redirect()


@login_required
@admin_required
def admin_undo_reject_registration(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('kind') != 'undo_reject_registration':
        messages.error(request, 'Undo link expired or is invalid.')
        return _registration_tab_redirect()

    registration = get_object_or_404(RegistrationRequest, id=payload['registration_id'])
    if registration.status != RegistrationRequest.Status.REJECTED:
        messages.error(request, 'Only rejected registrations can be restored to pending.')
        return _registration_tab_redirect()

    registration.status = RegistrationRequest.Status.PENDING
    registration.approved_by = None
    registration.decided_at = None
    registration.rejection_reason = ''
    registration.save(update_fields=['status', 'approved_by', 'decided_at', 'rejection_reason', 'updated_at'])
    log_action(request, 'REGISTRATION_RESTORED', 'RegistrationRequest', registration.id, registration.email, extra_data={'undo_registration_rejection': True, 'status': registration.status})
    messages.success(request, f'Registration for {registration.first_name} {registration.last_name} is pending again.')
    return _registration_tab_redirect()


@login_required
@admin_required
@require_POST
def admin_lift_messaging_suspension(request, user_id):
    user = get_object_or_404(User, id=user_id)
    previous_until = user.messaging_suspended_until
    if not previous_until:
        messages.error(request, 'This user does not have an active messaging suspension.')
        return redirect('admin_manage_users')
    user.messaging_suspended_until = None
    user.save(update_fields=['messaging_suspended_until'])
    token = _stash_undo_payload({
        'kind': 'undo_lift_messaging_suspension',
        'user_id': user.id,
        'previous_until': previous_until.isoformat(),
    })
    log_action(request, 'MESSAGING_SUSPENSION_LIFTED', 'User', user.id, user.get_full_name(), extra_data={'messaging_suspension_lifted': True})
    from accounts.otp_utils import send_transactional_email
    send_transactional_email(
        to_email=user.email,
        subject='BrightTrack — Your Messaging Suspension Has Been Lifted',
        text_content=(
            f'Dear {user.get_full_name()},\n\n'
            f'Your messaging access on BrightTrack has been restored by the school administrator.\n\n'
            f'You may now send and receive messages normally.\n\n'
            f'— BrightTrack School System'
        ),
    )
    messages.success(
        request,
        format_html(
            'Messaging suspension lifted for {}. Email sent. <a href="{}" class="underline font-semibold">Undo</a> ({}s)',
            user.get_full_name(),
            reverse('admin_undo_lift_messaging_suspension', args=[token]),
            UNDO_GRACE_SECONDS,
        )
    )
    return redirect('admin_manage_users')


@login_required
@admin_required
def admin_undo_lift_messaging_suspension(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('kind') != 'undo_lift_messaging_suspension':
        messages.error(request, 'Undo link expired or is invalid.')
        return redirect('admin_manage_users')

    user = get_object_or_404(User, id=payload['user_id'])
    restored_until = parse_datetime(payload.get('previous_until') or '')
    if not restored_until:
        messages.error(request, 'Previous suspension state could not be restored.')
        return redirect('admin_manage_users')

    user.messaging_suspended_until = restored_until
    user.save(update_fields=['messaging_suspended_until'])
    log_action(request, 'MESSAGING_SUSPENSION_RESTORED', 'User', user.id, user.get_full_name(), extra_data={'undo_lift_messaging_suspension': True})
    messages.success(request, f'Messaging suspension restored for {user.get_full_name()}.')
    return redirect('admin_manage_users')


@login_required
@admin_required
def admin_all_classes(request):
    classes = Class.objects.all().select_related('teacher').annotate(student_count=Count('students')).order_by('year_level', 'section', 'name')
    return render(request, 'admin/all_classes.html', {'classes': classes})


@login_required
@admin_required
def admin_view_class(request, class_id):
    cls = get_object_or_404(Class, id=class_id)
    students = cls.students.all().order_by('last_name', 'first_name')
    return render(request, 'admin/view_class.html', {'cls': cls, 'students': students})


@login_required
@admin_required
@require_POST
def admin_delete_class(request, class_id):
    cls = get_object_or_404(Class, id=class_id)
    name = cls.name
    payload = _serialize_class_for_undo(cls)
    payload.update({
        'kind': 'undo_delete_class',
        'redirect_to': 'admin_all_classes',
    })
    token = _stash_undo_payload(payload)
    log_action(request, 'CLASS_DELETED', 'Class', cls.id, name, extra_data={'deleted': True})
    cls.delete()
    messages.success(
        request,
        format_html(
            'Class "{}" deleted. <a href="{}" class="underline font-semibold">Undo</a> ({}s)',
            name,
            reverse('admin_undo_delete_class', args=[token]),
            UNDO_GRACE_SECONDS,
        )
    )
    return redirect('admin_all_classes')


@login_required
@admin_required
def admin_undo_delete_class(request, token):
    payload = _pop_undo_payload(token)
    if not payload or payload.get('kind') != 'undo_delete_class':
        messages.error(request, 'Undo link expired or is invalid.')
        return redirect('admin_all_classes')

    if Class.objects.filter(code=payload['class']['code']).exists():
        messages.error(request, 'Cannot restore this class because the class code is already in use.')
        return redirect('admin_all_classes')

    cls = _restore_class_from_payload(payload)
    log_action(request, 'CLASS_RESTORED', 'Class', cls.id, cls.name, extra_data={'undo_class_delete': True})
    messages.success(request, f'Class "{cls.name}" has been restored.')
    return _class_redirect_target(payload)


@login_required
@admin_required
def admin_audit_log(request):
    logs, filters = _apply_audit_log_filters(request)
    export_format = request.GET.get('export')
    if export_format in ['csv', 'pdf', 'docs']:
        rows = _audit_log_export_rows(logs)
        visual_headers = ['TIMESTAMP', 'ACTOR', 'ACTION', 'TARGET', 'IP', 'INTEGRITY', 'DETAILS']
        visual_rows = _audit_log_visual_rows(logs)
        headers = ['Timestamp', 'Actor', 'Action', 'Target Type', 'Target ID', 'Target Label', 'IP Address', 'Integrity', 'Details']

        if export_format == 'csv':
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(headers)
            writer.writerows(rows)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="audit-log.csv"'
            log_action(request, 'AUDIT_LOG_EXPORTED', 'AuditLog', None, 'Audit Log', extra_data={**filters, 'format': export_format})
            return response

        if export_format == 'docs':
            table_rows = ''.join(
                '<tr>' + ''.join(f'<td style="padding:8px;border:1px solid #e5e7eb;font-size:12px;">{html.escape(str(cell))}</td>' for cell in row) + '</tr>'
                for row in visual_rows
            )
            content = (
                '<html><head><meta charset="utf-8"></head><body>'
                '<h2 style="font-family:Arial,sans-serif;margin-bottom:12px;">Audit Log Export</h2>'
                '<table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;">'
                '<tr style="background:#f3f4f6;">' + ''.join(f'<th style="text-align:left;padding:8px;border:1px solid #e5e7eb;font-size:12px;">{h}</th>' for h in visual_headers) + '</tr>'
                f'{table_rows}</table></body></html>'
            )
            response = HttpResponse(content, content_type='application/msword')
            response['Content-Disposition'] = 'attachment; filename="audit-log.doc"'
            log_action(request, 'AUDIT_LOG_EXPORTED', 'AuditLog', None, 'Audit Log', extra_data={**filters, 'format': export_format})
            return response

        response = HttpResponse(_build_simple_pdf_table(visual_headers, visual_rows), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="audit-log.pdf"'
        log_action(request, 'AUDIT_LOG_EXPORTED', 'AuditLog', None, 'Audit Log', extra_data={**filters, 'format': export_format})
        return response

    paginator = Paginator(logs, 50)
    page = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('export', None)

    context = {
        'page_obj': page,
        'action_choices': AuditLog.ACTION_CHOICES,
        **filters,
        'filter_query': query_params.urlencode(),
    }
    return render(request, 'admin/audit_log.html', context)


@login_required
@superadmin_required
def admin_manage_admins(request):
    if request.method == 'POST':
        target_id = request.POST.get('user_id')
        new_role = request.POST.get('admin_role', '')
        target = get_object_or_404(User, id=target_id, role='admin')

        if target == request.user:
            messages.error(request, 'You cannot change your own admin role.')
            return redirect('admin_manage_admins')

        valid_roles = [r[0] for r in User.ADMIN_ROLE_CHOICES]
        if new_role not in valid_roles:
            messages.error(request, 'Invalid role.')
            return redirect('admin_manage_admins')

        old_role = target.admin_role
        target.admin_role = new_role
        target.save()

        log_action(request, 'ADMIN_ROLE_CHANGED', 'User', target.id, target.get_full_name(),
                   extra_data={'old_role': old_role, 'new_role': new_role})

        messages.success(request, f'{target.get_full_name()} role changed to {new_role}.')
        return redirect('admin_manage_admins')

    admins = User.objects.filter(role='admin').order_by('last_name', 'first_name')
    context = {'admins': admins, 'role_choices': User.ADMIN_ROLE_CHOICES}
    return render(request, 'admin/manage_admins.html', context)
