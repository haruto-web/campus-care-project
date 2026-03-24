from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponse, FileResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes
from academics.models import Class, Assignment, Submission, Attendance, Grade
from wellness.models import WellnessCheckIn, RiskAssessment, Alert, Intervention
from campus_care.validators import validate_image_upload
from .models import User, OTPCode, RegistrationRequest
from .otp_utils import send_otp_email, send_transactional_email
from .utils import log_action, hit_rate_limit, record_security_spike, run_background_task
from .decorators import teacher_owns_class


def _send_security_email(to_email, subject, lines):
    send_transactional_email(
        to_email=to_email,
        subject=subject,
        text_content="\n".join(lines),
    )


def _local_media_response(path):
    media_root = Path(settings.MEDIA_ROOT).resolve()
    file_path = (media_root / path).resolve()
    if media_root not in file_path.parents:
        raise Http404
    if not file_path.exists() or not file_path.is_file():
        raise Http404
    content_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
    return FileResponse(open(file_path, 'rb'), content_type=content_type)


@login_required
def protected_media_view(request, path):
    normalized_path = path.replace('\\', '/').lstrip('/')

    if normalized_path.startswith('profiles/'):
        return _local_media_response(normalized_path)

    if normalized_path.startswith('id_pictures/'):
        owner = User.objects.filter(id_picture=normalized_path).first()
        if owner and (request.user.id == owner.id or request.user.role in ['admin', 'counselor']):
            return _local_media_response(normalized_path)
        raise Http404

    if normalized_path.startswith('materials/'):
        from academics.models import Material
        material = Material.objects.select_related('class_obj', 'class_obj__teacher').filter(file=normalized_path).first()
        if material and (
            request.user.role in ['admin', 'counselor']
            or teacher_owns_class(request.user, material.class_obj)
            or material.class_obj.students.filter(id=request.user.id).exists()
        ):
            return _local_media_response(normalized_path)
        raise Http404

    if normalized_path.startswith('submissions/'):
        submission = Submission.objects.select_related('assignment__class_obj', 'student').filter(file=normalized_path).first()
        if submission and (
            request.user.role in ['admin', 'counselor']
            or request.user.id == submission.student_id
            or teacher_owns_class(request.user, submission.assignment.class_obj)
        ):
            return _local_media_response(normalized_path)
        raise Http404

    if normalized_path.startswith('message_attachments/'):
        from messaging.models import Message
        message = Message.objects.filter(attachment=normalized_path).first()
        if message and (
            request.user.role == 'admin'
            or message.conversation.participants.filter(id=request.user.id).exists()
        ):
            return _local_media_response(normalized_path)
        raise Http404

    raise Http404

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


from django.http import JsonResponse

@login_required
def notifications_poll(request):
    """Single endpoint polled by base.html every 5s for all notification counts."""
    if hit_rate_limit(request, 'notifications_poll', limit=120, window_seconds=60):
        return JsonResponse({'error': 'Too many requests'}, status=429)

    from messaging.models import Message
    from academics.models import Announcement, Submission
    from wellness.models import Alert
    from django.db.models import Q

    user = request.user
    data = {}

    # Unread messages
    data['messages'] = Message.objects.filter(
        conversation__participants=user, is_read=False
    ).exclude(sender=user).count()

    # New unread announcements (student/teacher)
    if user.role == 'student':
        classes = user.enrolled_classes.all()
        data['announcements'] = Announcement.objects.filter(
            Q(class_obj__in=classes) | Q(class_obj__isnull=True)
        ).exclude(read_by=user).count()
        # New grades (submissions graded in last 24h not yet seen)
        from datetime import timedelta
        from django.utils import timezone
        data['grades'] = Submission.objects.filter(
            student=user, score__isnull=False,
            graded_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
    else:
        data['announcements'] = 0
        data['grades'] = 0

    # Unread alerts (counselor/admin)
    if user.role in ['counselor', 'admin']:
        data['alerts'] = Alert.objects.filter(is_read=False, resolved=False).count()
    else:
        data['alerts'] = 0

    # Unread student notifications (intervention / concern)
    if user.role == 'student':
        from wellness.models import Notification as StudentNotif
        data['notifications'] = StudentNotif.objects.filter(recipient=user, is_read=False).count()
    else:
        data['notifications'] = 0

    data['total'] = data['messages'] + data['announcements'] + data['grades'] + data['alerts'] + data['notifications']
    return JsonResponse(data)


def fix_site_domain(request):
    """Temporary view to fix Site domain for OAuth - admin only"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponse('Forbidden', status=403)
    from django.contrib.sites.models import Site
    import os
    hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:8000')
    site = Site.objects.get_current()
    old = site.domain
    site.domain = hostname
    site.name = 'BrightTrack LMS'
    site.save()
    return HttpResponse(f'Site domain updated: {old} → {hostname}')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        from django.contrib.auth.password_validation import validate_password
        from django.contrib.auth.hashers import make_password

        # Rate limit: 5 attempts per IP per 10 minutes
        ip = request.META.get('REMOTE_ADDR')
        rate_key = f'reg_attempts_{ip}'
        attempts = cache.get(rate_key, 0)
        if attempts >= 5:
            messages.error(request, 'Too many registration attempts. Please try again later.')
            return render(request, 'accounts/register.html')
        cache.set(rate_key, attempts + 1, 600)

        student_number = request.POST.get('student_number', '').strip()
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip().title()
        last_name = request.POST.get('last_name', '').strip().title()
        year_level = request.POST.get('year_level', '').strip()
        section = request.POST.get('section', '').strip().title()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not student_number.isdigit() or len(student_number) != 12:
            return render(request, 'accounts/register.html', {
                'sn_error': 'Student number must be exactly 12 digits.',
                'student_number_val': student_number,
            })

        if not all([first_name, last_name, year_level]):
            messages.error(request, 'First name, last name, and year level are required.')
            return render(request, 'accounts/register.html')

        if year_level not in ('7', '8', '9', '10'):
            messages.error(request, 'Year level must be 7, 8, 9, or 10.')
            return render(request, 'accounts/register.html')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        try:
            validate_password(password)
        except DjangoValidationError as e:
            return render(request, 'accounts/register.html', {'password_errors': e.messages})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Registration failed. Please check your details or contact your administrator.')
            return render(request, 'accounts/register.html')

        existing_request = RegistrationRequest.objects.filter(
            student_number=student_number,
            email__iexact=email,
            status=RegistrationRequest.Status.PENDING
        ).first()
        if existing_request:
            messages.error(request, 'A registration request for this student is already pending admin approval.')
            return render(request, 'accounts/register.html')

        # Send OTP — don't create account yet
        otp = OTPCode.generate(email)
        try:
            send_otp_email(email, otp.code)
        except Exception:
            import logging
            logging.getLogger(__name__).error('OTP email failed during registration')
            messages.error(request, 'Failed to send verification code. Please try again.')
            return render(request, 'accounts/register.html')

        request.session['otp_email'] = email
        request.session['otp_purpose'] = 'register'
        request.session['reg_data'] = {
            'student_number': student_number,
            'first_name': first_name,
            'last_name': last_name,
            'year_level': year_level,
            'section': section,
            'password_hash': make_password(password),
        }
        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


def otp_request_view(request):
    """Step 1: Student enters email only — always sends OTP."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email or '@' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'accounts/otp_request.html')

        # Rate limit: max 3 OTP sends per email per 15 minutes
        rate_key = f'otp_send_{email}'
        send_count = cache.get(rate_key, 0)
        if send_count >= 3:
            messages.error(request, 'Too many verification requests. Please wait 15 minutes before trying again.')
            return render(request, 'accounts/otp_request.html')

        otp = OTPCode.generate(email)
        try:
            send_otp_email(email, otp.code)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f'OTP email failed: {e}')
            messages.error(request, 'Failed to send verification code. Please try again later.')
            return render(request, 'accounts/otp_request.html')

        cache.set(rate_key, send_count + 1, 900)  # 15-minute window
        request.session['otp_email'] = email
        request.session.pop('otp_purpose', None)
        return redirect('otp_verify')

    return render(request, 'accounts/otp_request.html')


def otp_verify_view(request):
    """OTP verify — used for login, new registration, and forgot password."""
    email = request.session.get('otp_email')
    if not email:
        return redirect('otp_request')

    if request.method == 'POST':
        # Rate limit: max 5 verify attempts per email per 30 minutes
        attempt_key = f'otp_attempts_{email}'
        attempts = cache.get(attempt_key, 0)
        if attempts >= 5:
            messages.error(request, 'Too many failed attempts. Please wait 30 minutes before trying again.')
            return render(request, 'accounts/otp_verify.html', {'email': email})

        entered = request.POST.get('code', '').strip()
        otp = OTPCode.objects.filter(
            contact_value=email, code=entered, is_used=False
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            cache.set(attempt_key, attempts + 1, 1800)  # 30-minute lockout window
            messages.error(request, 'Invalid or expired code. Please try again.')
            return render(request, 'accounts/otp_verify.html', {'email': email})

        otp.is_used = True
        otp.save()
        request.session['otp_verified'] = True
        cache.delete(attempt_key)  # Reset attempts on success

        if request.session.get('otp_purpose') == 'reset':
            return redirect('otp_reset_password')

        existing = User.objects.filter(email=email, role='student').first()
        if existing:
            return redirect('otp_login_password')

        return redirect('otp_register')

    return render(request, 'accounts/otp_verify.html', {'email': email})


def otp_login_password_view(request):
    """Existing student enters password after OTP verified."""
    if not request.session.get('otp_verified'):
        return redirect('otp_request')

    email = request.session.get('otp_email')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        try:
            u = User.objects.get(email=email, role='student')
            user = authenticate(request, username=u.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            for key in ['otp_email', 'otp_verified']:
                request.session.pop(key, None)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
        else:
            messages.error(request, 'Incorrect password.')

    return render(request, 'accounts/otp_login_password.html', {'email': email})


def otp_forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        rate_key = f'forgot_password_send_{email}'
        send_count = cache.get(rate_key, 0)
        if send_count >= 3:
            messages.error(request, 'Too many reset requests. Please wait 15 minutes before trying again.')
            return render(request, 'accounts/otp_forgot_password.html')

        user = User.objects.filter(email=email).first()
        if not user:
            messages.success(request, 'If an account exists for that email, a reset code will be sent.')
            return render(request, 'accounts/otp_forgot_password.html')

        otp = OTPCode.generate(email)
        try:
            send_otp_email(email, otp.code)
        except Exception:
            import logging
            logging.getLogger(__name__).error('OTP email failed during forgot password')
            messages.error(request, 'Failed to send code. Please try again later.')
            return render(request, 'accounts/otp_forgot_password.html')

        cache.set(rate_key, send_count + 1, 900)
        _send_security_email(
            email,
            'BrightTrack Password Reset Requested',
            [
                f'Dear {user.get_full_name() or user.email},',
                '',
                'A password reset code was requested for your BrightTrack account.',
                'If this was you, you can continue using the verification code that was just sent.',
                'If this was not you, please ignore this message and consider changing your password after logging in.',
            ],
        )
        request.session['otp_email'] = email
        request.session['otp_purpose'] = 'reset'
        return redirect('verify_otp')

    return render(request, 'accounts/otp_forgot_password.html')


def otp_reset_password_view(request):
    if not request.session.get('otp_verified') or request.session.get('otp_purpose') != 'reset':
        return redirect('login')

    email = request.session.get('otp_email')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/otp_reset_password.html')

        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password)
        except DjangoValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, 'accounts/otp_reset_password.html')

        user = User.objects.filter(email=email).first()
        if not user:
            return redirect('login')
        user.set_password(password)
        user.save()
        log_action(request, 'PASSWORD_RESET', 'User', user.id, user.get_full_name())
        _send_security_email(
            user.email,
            'BrightTrack Password Changed',
            [
                f'Dear {user.get_full_name() or user.email},',
                '',
                'Your BrightTrack password was changed successfully.',
                f'Time: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
                f'IP Address: {request.META.get("REMOTE_ADDR", "unknown")}',
                '',
                'If this was not you, please contact an administrator immediately.',
            ],
        )

        for key in ['otp_email', 'otp_verified', 'otp_purpose']:
            request.session.pop(key, None)

        messages.success(request, 'Password reset successfully. Please log in.')
        return redirect('login')

    return render(request, 'accounts/otp_reset_password.html')


def otp_register_view(request):
    """New student fills in name + password after OTP verified."""
    if not request.session.get('otp_verified'):
        return redirect('otp_request')

    email = request.session.get('otp_email')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/otp_register.html', {'email': email})

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/otp_register.html', {'email': email})

        # Validate password strength using Django validators
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_password(password)
        except DjangoValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, 'accounts/otp_register.html', {'email': email})

        import uuid
        base = f"{first_name.lower()}{last_name.lower()}"
        username = f"{base}{str(uuid.uuid4())[:4]}"
        while User.objects.filter(username=username).exists():
            username = f"{base}{str(uuid.uuid4())[:4]}"

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='student',
        )
        user.set_password(password)
        user.save()

        for key in ['otp_email', 'otp_verified']:
            request.session.pop(key, None)

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Account created! Please complete your profile.')
        return redirect('complete_profile')

    return render(request, 'accounts/otp_register.html', {'email': email})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        attempt_key = f'login_attempts_{ip}_{email}'
        attempts = cache.get(attempt_key, 0)

        if attempts >= 5:
            messages.error(request, 'Too many login attempts. Please wait 10 minutes before trying again.')
            return render(request, 'accounts/login.html')

        try:
            u = User.objects.get(email=email)
            user = authenticate(request, username=u.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            otp = OTPCode.generate(email)
            try:
                send_otp_email(email, otp.code)
            except Exception:
                import logging
                logging.getLogger(__name__).error('OTP email failed during login')
                messages.error(request, 'Failed to send verification code. Please try again.')
                return render(request, 'accounts/login.html')
            cache.delete(attempt_key)
            request.session['otp_user_id'] = user.id
            request.session['otp_email'] = email
            request.session['otp_purpose'] = 'login'
            return redirect('verify_otp')
        else:
            cache.set(attempt_key, attempts + 1, 600)
            record_security_spike(f'failed_login:{ip}', threshold=5, window_seconds=600)
            log_action(request, 'LOGIN_FAILED', 'User', None, email)
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def verify_otp_view(request):
    purpose = request.session.get('otp_purpose')
    email = request.session.get('otp_email')

    if not email or purpose not in ('login', 'register', 'reset'):
        return redirect('login')

    if request.method == 'POST':
        attempt_key = f'otp_attempts_{email}'
        attempts = cache.get(attempt_key, 0)
        if attempts >= 5:
            messages.error(request, 'Too many failed attempts. Please wait 30 minutes.')
            return render(request, 'accounts/verify_otp.html', {'email': email, 'purpose': purpose})

        code = request.POST.get('code', '').strip()
        otp = OTPCode.objects.filter(
            contact_value=email, code=code, is_used=False
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            cache.set(attempt_key, attempts + 1, 1800)
            messages.error(request, 'Invalid or expired code.')
            return render(request, 'accounts/verify_otp.html', {'email': email, 'purpose': purpose})

        otp.is_used = True
        otp.save()
        cache.delete(attempt_key)

        if purpose == 'login':
            user_id = request.session.get('otp_user_id')
            if not user_id:
                return redirect('login')
            user = User.objects.get(id=user_id)
            for key in ['otp_user_id', 'otp_email', 'otp_purpose']:
                request.session.pop(key, None)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            log_action(request, 'LOGIN', 'User', user.id, user.get_full_name())
            if user.role in ['teacher', 'counselor', 'admin']:
                _send_security_email(
                    user.email,
                    'BrightTrack New Login Alert',
                    [
                        f'Dear {user.get_full_name() or user.email},',
                        '',
                        f'A new login to your BrightTrack account was completed as {user.role}.',
                        f'Time: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
                        f'IP Address: {request.META.get("REMOTE_ADDR", "unknown")}',
                        '',
                        'If this was not you, please change your password and contact an administrator immediately.',
                    ],
                )
            return redirect('dashboard')

        elif purpose == 'register':
            from django.db import transaction
            reg = request.session.get('reg_data', {})
            if not reg:
                messages.error(request, 'Registration session expired. Please try again.')
                return redirect('register')
            with transaction.atomic():
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'An account with this email already exists.')
                    return redirect('register')
                registration, _ = RegistrationRequest.objects.update_or_create(
                    student_number=reg['student_number'],
                    email=email,
                    defaults={
                        'first_name': reg['first_name'],
                        'last_name': reg['last_name'],
                        'year_level': reg['year_level'],
                        'section': reg.get('section', ''),
                        'password_hash': reg['password_hash'],
                        'status': RegistrationRequest.Status.PENDING,
                        'approved_by': None,
                        'decided_at': None,
                        'rejection_reason': '',
                    }
                )
            log_action(request, 'REGISTRATION_SUBMITTED', 'RegistrationRequest', registration.id, registration.email)
            for key in ['otp_email', 'otp_purpose', 'reg_data']:
                request.session.pop(key, None)
            messages.success(request, 'Registration submitted. Please wait for admin approval. We will email you once approved or rejected.')
            return redirect('login')

        elif purpose == 'reset':
            request.session['otp_verified'] = True
            return redirect('otp_reset_password')

    return render(request, 'accounts/verify_otp.html', {'email': email, 'purpose': purpose})

@require_POST
def logout_view(request):
    log_action(request, 'LOGOUT', 'User', request.user.id, request.user.get_full_name())
    logout(request)
    return redirect('landing')

@login_required
def dashboard_view(request):
    user = request.user

    if user.role == 'student':
        # 7-day skip enforcement
        if not user.profile_completed:
            return redirect('complete_profile')
        if user.profile_skipped_at and not user.profile_completed:
            from datetime import timedelta
            if timezone.now() > user.profile_skipped_at + timedelta(days=7):
                user.profile_completed = False
                user.save(update_fields=['profile_completed'])
                return redirect('complete_profile')
        return student_dashboard(request)
    elif user.role == 'teacher':
        return teacher_dashboard(request)
    elif user.role == 'counselor':
        return counselor_dashboard(request)
    else:
        return admin_dashboard(request)

@login_required
def student_dashboard(request):
    cache_key = f'dashboard:student:{request.user.id}'
    cached_context = cache.get(cache_key)
    if cached_context:
        return render(request, 'dashboard/student_dashboard.html', cached_context)

    user = request.user
    classes = user.enrolled_classes.all()
    
    # Attach missing assignments per class for the dashboard panel
    submitted_ids = Submission.objects.filter(student=user).values_list('assignment_id', flat=True)
    from django.utils import timezone as tz
    now = tz.now()
    for cls in classes:
        cls.missing_for_student = cls.assignments.filter(
            due_date__lt=now
        ).exclude(id__in=submitted_ids)
    
    # Get upcoming assignments
    assignments = Assignment.objects.filter(
        class_obj__in=classes,
        due_date__gte=now
    ).order_by('due_date')[:5]
    
    # Get recent announcements (all, with read status)
    from academics.models import Announcement
    announcements = Announcement.objects.filter(
        Q(class_obj__in=classes) | Q(class_obj__isnull=True)
    ).order_by('-created_at')[:6]
    for a in announcements:
        a.is_read = a.read_by.filter(id=user.id).exists()
    
    # Get recently graded assignments (last 5)
    recently_graded = Submission.objects.filter(
        student=user,
        score__isnull=False
    ).select_related('assignment', 'assignment__class_obj').order_by('-graded_at')[:5]
    
    # Get last wellness check-in
    last_checkin = WellnessCheckIn.objects.filter(student=user).order_by('-date').first()
    
    # Count missing assignments
    all_assignments = Assignment.objects.filter(class_obj__in=classes)
    missing_assignments = all_assignments.exclude(id__in=submitted_ids).count()
    
    context = {
        'classes': classes,
        'assignments': assignments,
        'announcements': announcements,
        'recently_graded': recently_graded,
        'last_checkin': last_checkin,
        'missing_assignments': missing_assignments,
    }
    cache.set(cache_key, context, 120)
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    cache_key = f'dashboard:teacher:{request.user.id}'
    cached_context = cache.get(cache_key)
    if cached_context:
        return render(request, 'dashboard/teacher_dashboard.html', cached_context)

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
    
    # Get recent submissions (last 10) grouped by class - only from teacher's classes
    recent_submissions = Submission.objects.filter(
        assignment__class_obj__in=classes
    ).select_related('student', 'assignment', 'assignment__class_obj').order_by('-submitted_at')[:15]
    
    # Group submissions by class
    from collections import defaultdict
    submissions_by_class_dict = defaultdict(list)
    for submission in recent_submissions:
        submissions_by_class_dict[submission.assignment.class_obj].append(submission)
    
    # Convert to list format for template (limit 3 submissions per class)
    submissions_by_class = []
    for class_obj, submissions in submissions_by_class_dict.items():
        submissions_by_class.append({
            'class': class_obj,
            'submissions': submissions[:3]  # Limit to 3 per class
        })
    
    # Section-based breakdowns
    from collections import defaultdict
    
    # Students by section
    students_by_section = defaultdict(int)
    for student in students:
        section = student.section or 'No Section'
        students_by_section[section] += 1
    
    # At-risk by section
    atrisk_by_section = defaultdict(int)
    for student in at_risk_students:
        section = student.section or 'No Section'
        atrisk_by_section[section] += 1
    
    # Pending grades by section
    pending_by_section = defaultdict(int)
    pending_submissions = Submission.objects.filter(
        assignment__class_obj__in=classes,
        score__isnull=True
    ).select_related('student')
    for submission in pending_submissions:
        section = submission.student.section or 'No Section'
        pending_by_section[section] += 1
    
    # Convert to list format for template
    students_by_section_list = [{'section': k, 'count': v} for k, v in students_by_section.items()]
    atrisk_by_section_list = [{'section': k, 'count': v} for k, v in atrisk_by_section.items()]
    pending_by_section_list = [{'section': k, 'count': v} for k, v in pending_by_section.items()]
    
    context = {
        'classes': classes,
        'at_risk_students': at_risk_students,
        'total_students': len(students),
        'pending_grades': pending_grades,
        'at_risk_count': len(at_risk_students),
        'recent_submissions': recent_submissions,
        'submissions_by_class': submissions_by_class,
        'students_by_section': students_by_section_list,
        'atrisk_by_section': atrisk_by_section_list,
        'pending_by_section': pending_by_section_list,
    }
    cache.set(cache_key, context, 120)
    return render(request, 'dashboard/teacher_dashboard.html', context)

@login_required
def counselor_dashboard(request):
    cache_key = f'dashboard:counselor:{request.user.id}'
    cached_context = cache.get(cache_key)
    if cached_context:
        return render(request, 'dashboard/counselor_dashboard.html', cached_context)

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
        scheduled_date__gte=timezone.now()
    ).order_by('scheduled_date')[:5]
    
    pending_interventions = Intervention.objects.filter(status='scheduled').count()
    
    # Section-based breakdowns
    from collections import defaultdict
    
    # High risk by section
    highrisk_by_section = defaultdict(int)
    high_risk_assessments = RiskAssessment.objects.filter(risk_level='high').select_related('student')
    for assessment in high_risk_assessments:
        section = assessment.student.section or 'No Section'
        highrisk_by_section[section] += 1
    
    # Medium risk by section
    mediumrisk_by_section = defaultdict(int)
    medium_risk_assessments = RiskAssessment.objects.filter(risk_level='medium').select_related('student')
    for assessment in medium_risk_assessments:
        section = assessment.student.section or 'No Section'
        mediumrisk_by_section[section] += 1
    
    # Convert to list format for template
    highrisk_by_section_list = [{'section': k, 'count': v} for k, v in highrisk_by_section.items()]
    mediumrisk_by_section_list = [{'section': k, 'count': v} for k, v in mediumrisk_by_section.items()]
    
    context = {
        'high_risk_students': high_risk_students,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'alerts': alerts,
        'unread_alerts': unread_alerts,
        'upcoming_interventions': upcoming_interventions,
        'pending_interventions': pending_interventions,
        'highrisk_by_section': highrisk_by_section_list,
        'mediumrisk_by_section': mediumrisk_by_section_list,
    }
    cache.set(cache_key, context, 120)
    return render(request, 'dashboard/counselor_dashboard.html', context)

@login_required
def admin_dashboard(request):
    from django.db.models import Count
    from datetime import timedelta
    from django.core.management import call_command

    def _refresh_risk_assessments():
        try:
            call_command('calculate_risk')
            cache.set('dashboard:risk_last_refresh', timezone.now().isoformat(), 86400)
        except Exception:
            pass
        finally:
            cache.delete('dashboard:risk_refresh_running')

    # Auto-calculate risk assessments if none exist or if last calculation was > 1 day ago
    latest_assessment = RiskAssessment.objects.order_by('-date').first()
    refresh_lock = cache.get('dashboard:risk_refresh_running')
    if (not latest_assessment or (timezone.now().date() - latest_assessment.date).days > 0) and not refresh_lock:
        cache.set('dashboard:risk_refresh_running', True, 300)
        run_background_task(_refresh_risk_assessments)

    cache_key = 'dashboard:admin'
    cached_context = cache.get(cache_key)
    if cached_context:
        return render(request, 'dashboard/admin_dashboard.html', cached_context)

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
    activity_labels = []
    activity_data = []
    
    for i in range(6):
        date = timezone.now() - timedelta(days=i*5)
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
    cache.set(cache_key, context, 120)
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        if hit_rate_limit(request, 'accounts_profile_update', limit=15, window_seconds=600):
            messages.error(request, 'Too many profile updates. Please wait before trying again.')
            return redirect('profile')
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.phone = request.POST.get('phone', '')
        
        # Protect email changes — require re-verification
        new_email = request.POST.get('email', '').strip()
        if new_email and new_email != request.user.email:
            messages.warning(request, 'Email changes require verification. Your email was not updated.')
        
        if request.FILES.get('profile_picture'):
            try:
                validate_image_upload(request.FILES['profile_picture'])
                request.user.profile_picture = request.FILES['profile_picture']
            except DjangoValidationError as e:
                messages.warning(request, f'Profile picture rejected: {e.message}')
            except Exception:
                messages.warning(request, 'Profile picture upload failed. Other changes saved.')
        
        try:
            request.user.save()
        except Exception:
            request.user.profile_picture = None
            request.user.save()
            messages.warning(request, 'Profile picture upload failed. Other changes saved.')
            return redirect('profile')
        log_action(request, 'PROFILE_UPDATED', 'User', request.user.id, request.user.get_full_name())
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
    if request.user.role == 'teacher' and not request.user.classes_taught.filter(students=student).exists():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    log_action(
        request,
        'STUDENT_PROFILE_VIEWED',
        'User',
        student.id,
        student.get_full_name(),
        extra_data={'viewer_role': request.user.role},
    )
    
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
        total = attendance_records.count()
        present_or_late = attendance_records.filter(status__in=['present', 'late']).count()
        attendance_rate = round((present_or_late / total) * 100, 1)
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
        attendance_records = Attendance.objects.filter(student=student, class_obj__in=my_classes)
        
        if attendance_records.exists():
            total = attendance_records.count()
            present_or_late = attendance_records.filter(status__in=['present', 'late']).count()
            attendance_rate = round((present_or_late / total) * 100, 1)
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
    if request.user.profile_completed and not request.user.profile_skipped_at:
        return redirect('dashboard')

    from datetime import timedelta
    skip_allowed = True
    if request.user.profile_skipped_at:
        if timezone.now() > request.user.profile_skipped_at + timedelta(days=7):
            skip_allowed = False

    if request.GET.get('skip') and skip_allowed:
        if not request.user.profile_skipped_at:
            request.user.profile_skipped_at = timezone.now()
        request.user.profile_completed = True
        request.user.save(update_fields=['profile_completed', 'profile_skipped_at'])
        log_action(request, 'PROFILE_COMPLETED', 'User', request.user.id, request.user.get_full_name(), extra_data={'skipped': True})
        return redirect('dashboard')

    if request.method == 'POST':
        if hit_rate_limit(request, 'accounts_complete_profile', limit=10, window_seconds=600):
            messages.error(request, 'Too many profile submissions. Please wait before trying again.')
            return redirect('complete_profile')
        user = request.user
        user.phone = request.POST.get('phone', '')
        user.date_of_birth = request.POST.get('date_of_birth') if request.POST.get('date_of_birth') else None

        if user.role == 'student':
            user.section = request.POST.get('section', '')
            user.address = request.POST.get('address', '')
            user.guardian_name = request.POST.get('guardian_name', '')
            user.guardian_relation = request.POST.get('guardian_relation', '')
            user.guardian_occupation = request.POST.get('guardian_occupation', '')
            if request.POST.get('year_level'):
                user.year_level = request.POST.get('year_level')
            if request.FILES.get('id_picture'):
                try:
                    validate_image_upload(request.FILES['id_picture'])
                    user.id_picture = request.FILES['id_picture']
                except Exception:
                    messages.warning(request, 'ID picture upload failed. Other changes saved.')
        if request.FILES.get('profile_picture'):
            try:
                validate_image_upload(request.FILES['profile_picture'])
                user.profile_picture = request.FILES['profile_picture']
            except Exception:
                messages.warning(request, 'Profile picture upload failed. Other changes saved.')

        user.profile_completed = True
        user.profile_skipped_at = None
        try:
            user.save()
        except Exception:
            user.profile_picture = None
            user.id_picture = None
            user.save()
            messages.warning(request, 'File uploads failed, but profile was saved.')

        if user.role == 'student' and user.section and user.year_level:
            section_classes = Class.objects.filter(
                section__iexact=user.section,
                year_level=user.year_level
            )
            for section_class in section_classes:
                section_class.students.add(user)

        log_action(request, 'PROFILE_COMPLETED', 'User', user.id, user.get_full_name(), extra_data={'skipped': False})
        messages.success(request, 'Profile completed successfully!')
        return redirect('dashboard')

    if request.user.role == 'student':
        template = 'accounts/complete_profile_student.html'
    elif request.user.role == 'teacher':
        template = 'accounts/complete_profile_teacher.html'
    elif request.user.role == 'counselor':
        template = 'accounts/complete_profile_counselor.html'
    else:
        template = 'accounts/complete_profile.html'

    return render(request, template, {'skip_allowed': skip_allowed})
