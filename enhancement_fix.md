# BrightTrack LMS — Enhancement & Fix Workflow

> **Date:** March 8, 2026 | **Status:** Production System — Zero-Downtime Plan  
> **Approach:** 5-Phase rollout, backward-compatible, per-entity validation

---

## Execution Phases Overview

| Phase | Focus | Risk | Duration |
|-------|-------|------|----------|
| **1** | Critical Security Hardening | 🔴 Highest | Day 1-2 |
| **2** | Medium Security + Code Cleanup | 🟡 Medium | Day 3-5 |
| **3** | Shared Utilities & Deduplication | 🟢 Low | Day 6-8 |
| **4** | UI/UX Foundation & Design System | 🟡 Medium | Day 9-16 |
| **5** | Per-Entity UI Rollout & Polish | 🟡 Medium | Day 17-25 |

---

## PHASE 1 — Critical Security Hardening (Day 1-2)

> **Goal:** Patch all 6 CRITICAL vulnerabilities with zero downtime. No UI changes.

### 1.1 settings.py — Configuration Lockdown

**Current → New Comparison:**

```python
# ❌ CURRENT (settings.py:26-29)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-(p*_xzor)...')
DEBUG = config('DEBUG', default=True, cast=bool)

# ✅ NEW — crash on missing secret, safe default for debug
SECRET_KEY = config('SECRET_KEY')  # No default — app refuses to start without it
DEBUG = config('DEBUG', default=False, cast=bool)  # Safe default
```

**Add security headers (append to settings.py):**

```python
# --- Security Headers (Phase 1) ---
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
```

**Remove duplicate context processor (settings.py:92):** Delete second `django.template.context_processors.request`.

**Simulation:** Deploy with env variables already set → zero change in behavior. Without env → app crashes early with clear error instead of running insecure.

---

### 1.2 OTP Rate Limiting & Brute-Force Protection

**Current → New Comparison:**

| Aspect | Current | New |
|--------|---------|-----|
| OTP send rate | Unlimited | 3 per email per 15 min |
| OTP verify attempts | Unlimited | 5 attempts, then lockout 30 min |
| OTP length | 6 digits | 6 digits (unchanged) |
| OTP expiry | 10 min | 10 min (unchanged) |

**Implementation (accounts/views.py):**

```python
# NEW: Add to otp_request_view, before OTPCode.generate()
from django.core.cache import cache

def _check_otp_rate_limit(email):
    """Returns True if rate-limited."""
    key = f'otp_send_{email}'
    count = cache.get(key, 0)
    if count >= 3:
        return True
    cache.set(key, count + 1, 900)  # 15-min window
    return False

def _check_otp_verify_limit(email):
    """Returns True if locked out."""
    key = f'otp_attempts_{email}'
    attempts = cache.get(key, 0)
    if attempts >= 5:
        return True
    cache.set(key, attempts + 1, 1800)  # 30-min lockout
    return False
```

**Simulation:** Existing users unaffected (normal flow uses 1 OTP). Attackers hit rate limit after 3 sends or 5 verify attempts per 15/30 min.

---

### 1.3 Destructive Admin Endpoints

**Current → New Comparison:**

| Endpoint | Current | New |
|----------|---------|-----|
| `admin_delete_user` | GET allowed, no confirm | POST only + modal confirmation |
| `admin_cleanup_users` | 1-click mass delete | Require typed confirmation phrase + audit log |
| `admin_create_superuser` | No password validation | Django password validators + re-auth required |

**Implementation (accounts/admin_views.py):**

```python
# admin_delete_user — require POST
@login_required
@require_POST  # NEW: import from django.views.decorators.http
def admin_delete_user(request, user_id):
    # ... existing logic unchanged ...

# admin_cleanup_users — require confirmation phrase
@login_required
@require_POST
def admin_cleanup_users(request):
    confirmation = request.POST.get('confirmation', '')
    if confirmation != 'DELETE ALL USERS':
        messages.error(request, 'Please type the confirmation phrase exactly.')
        return redirect('admin_cleanup_users')
    # Log the action
    import logging
    logger = logging.getLogger('brighttrack.audit')
    logger.critical(f'MASS DELETION by {request.user.username} at {timezone.now()}')
    # ... existing deletion logic ...

# admin_create_superuser — validate password
from django.contrib.auth.password_validation import validate_password
@login_required
@require_POST
def admin_create_superuser(request):
    password = request.POST.get('password')
    try:
        validate_password(password)
    except ValidationError as e:
        messages.error(request, ' '.join(e.messages))
        return render(request, 'admin/create_superuser.html')
    # ... existing creation logic ...
```

**Simulation:** Admin UI adds confirmation modals. Templates updated to use POST forms. All existing admin workflows preserved — just safer.

---

### 1.4 Logout CSRF Fix

```python
# ❌ CURRENT
def logout_view(request):
    logout(request)
    return redirect('login')

# ✅ NEW — POST only
@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')
```

**Template change:** All logout links become `<form method="POST">{% csrf_token %}<button>Logout</button></form>`.

---

## PHASE 2 — Medium Security + Input Validation (Day 3-5)

### 2.1 File Upload Validation (All Modules)

**Create `campus_care/validators.py` (NEW file):**

```python
import os
from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip'}
ALLOWED_SUBMISSION_EXTENSIONS = ALLOWED_DOCUMENT_EXTENSIONS | {'.py', '.java', '.cpp', '.html', '.css', '.js'}
MAX_FILE_SIZE_MB = 10

def validate_file_upload(file, allowed_extensions, max_size_mb=MAX_FILE_SIZE_MB):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'File type {ext} not allowed. Allowed: {", ".join(sorted(allowed_extensions))}')
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File too large. Maximum size: {max_size_mb}MB.')

def validate_image_upload(file):
    validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, max_size_mb=5)

def validate_document_upload(file):
    validate_file_upload(file, ALLOWED_DOCUMENT_EXTENSIONS)

def validate_submission_upload(file):
    validate_file_upload(file, ALLOWED_SUBMISSION_EXTENSIONS)
```

**Apply across all upload points:**

| View | File | Validator |
|------|------|-----------|
| `profile_view` | `accounts/views.py` | `validate_image_upload` for profile_picture |
| `complete_profile_view` | `accounts/views.py` | `validate_image_upload` for profile_picture, id_picture |
| `submit_assignment` | `academics/views.py` | `validate_submission_upload` |
| `upload_material` | `academics/views.py` | `validate_document_upload` |
| `conversation` / `new_message` | `messaging/views.py` | `validate_document_upload` for attachments |

**Simulation:** Users uploading valid files (images, PDFs, docs) → no change. Users uploading `.exe`, `.php` → rejected with clear error message.

---

### 2.2 Score Validation (academics/views.py)

```python
# ❌ CURRENT (grade_submission)
submission.score = int(score) if score else None

# ✅ NEW
try:
    score_val = int(score)
except (ValueError, TypeError):
    messages.error(request, 'Invalid score value.')
    return redirect(...)
if score_val < 0 or score_val > submission.assignment.total_points:
    messages.error(request, f'Score must be between 0 and {submission.assignment.total_points}.')
    return redirect(...)
submission.score = score_val
```

### 2.3 Password Validation on Registration

```python
# Add to register_view AND otp_register_view
from django.contrib.auth.password_validation import validate_password
try:
    validate_password(password)
except ValidationError as e:
    for msg in e.messages:
        messages.error(request, msg)
    return render(request, template)
```

### 2.4 Profile Email Change Protection

```python
# accounts/views.py — profile_view POST handler
new_email = request.POST.get('email')
if new_email != request.user.email:
    messages.warning(request, 'Email changes require verification. Email unchanged.')
    # Don't update email — or trigger OTP re-verification flow
else:
    request.user.email = new_email
```

### 2.5 AI Prompt Sanitization

```python
# ml_models/gemini_client.py — add sanitizer
import re

def _sanitize_for_prompt(text):
    """Strip control characters and limit length."""
    if not text:
        return ''
    text = re.sub(r'[^\w\s.,!?;:\'"-]', '', str(text))
    return text[:500]  # Cap at 500 chars
```

### 2.6 Error Response Sanitization

```python
# ai_assistant/views.py — replace all str(e) in error responses
except Exception as e:
    import logging
    logging.getLogger('brighttrack').error(f'AI error: {e}', exc_info=True)
    return JsonResponse({'error': 'An internal error occurred. Please try again.'}, status=500)
```

### 2.7 Message Poll Endpoint Fix

```python
# messaging/views.py:98
try:
    after_id = int(request.GET.get('after', 0))
except (ValueError, TypeError):
    after_id = 0
```

### 2.8 Timezone Fix (wellness/views.py)

```python
# Replace all datetime.now() with timezone.now()
# Lines 432, 439, 506, 510 in wellness/views.py
# Lines 54, 150-151, 244, 266 in ai_assistant/views.py
```

---

## PHASE 3 — Code Cleanup & Deduplication (Day 6-8)

### 3.1 Create Shared Decorators (`accounts/decorators.py` — NEW)

```python
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, 'Permission denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def teacher_owns_class(view_func):
    @wraps(view_func)
    def wrapper(request, class_id, *args, **kwargs):
        from academics.models import Class
        class_obj = get_object_or_404(Class, id=class_id)
        if request.user.role != 'teacher' or class_obj.teacher != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('dashboard')
        request.class_obj = class_obj  # Attach to request
        return view_func(request, class_id, *args, **kwargs)
    return wrapper
```

**Apply across:** 6 student views in `academics/views.py`, 10+ teacher views in `academics/views.py`.

### 3.2 Create Shared Utilities (`accounts/utils.py` — NEW)

```python
def calculate_attendance_rate(student, class_obj=None):
    from academics.models import Attendance
    qs = Attendance.objects.filter(student=student)
    if class_obj:
        qs = qs.filter(class_obj=class_obj)
    total = qs.count()
    if total == 0:
        return None
    present = qs.filter(status='present').count()
    return round((present / total) * 100, 1)

def get_risk_counts():
    from wellness.models import RiskAssessment
    return {
        'high': RiskAssessment.objects.filter(risk_level='high').values('student').distinct().count(),
        'medium': RiskAssessment.objects.filter(risk_level='medium').values('student').distinct().count(),
        'low': RiskAssessment.objects.filter(risk_level='low').values('student').distinct().count(),
    }

def get_teacher_stats(teacher):
    from academics.models import Class, Submission
    from wellness.models import RiskAssessment
    classes = Class.objects.filter(teacher=teacher)
    students = set()
    for cls in classes:
        students.update(cls.students.all())
    at_risk = [s for s in students if RiskAssessment.objects.filter(
        student=s, risk_level='high').exists()]
    pending = Submission.objects.filter(
        assignment__class_obj__in=classes, score__isnull=True).count()
    return {'classes': classes, 'students': students,
            'at_risk': at_risk, 'pending_grades': pending}
```

### 3.3 Cleanup Checklist

| Item | Action | Files Affected |
|------|--------|---------------|
| Remove `register_view` | Delete function + URL route | `accounts/views.py`, `accounts/urls.py` |
| Remove unused `Grade` model | Delete model (migration needed) | `academics/models.py` |
| Remove `filter_message_content` | Remove unused function | `messaging/content_filter.py` |
| Remove `WellnessCheckIn.comments` | Migration to drop column | `wellness/models.py` |
| Remove `base_minimal.html` | Delete file | `templates/` |
| Remove `profile_counselor.html` | Delete file | `templates/accounts/` |
| Move `fix_site_domain` to management command | Create `accounts/management/commands/fix_site.py` | `accounts/views.py`, `accounts/urls.py` |
| Merge `announcement_views.py` into `views.py` | Move 2 functions | `academics/` |
| Combine 3 RiskAssessment signal handlers | Merge into 1 handler | `wellness/signals.py` |
| Fix `Assignment.points` → `.total_points` | Fix attribute name | `ml_models/utils.py:98` |
| Move top-level docs to `docs/` | Move files | Project root |

**Migration safety:** All model changes require `makemigrations` + `migrate`. The `Grade` model removal needs data verification first — confirm no FK references remain.

---

## PHASE 4 — UI/UX Foundation & Design System (Day 9-16)

### 4.1 Design System Setup

**Create `static/css/design-system.css` (NEW):**

Core tokens (colors, typography, spacing, shadows) as CSS custom properties. All templates reference these variables instead of hardcoded Tailwind colors.

**Create `templates/components/` directory (NEW) with partials:**

| Partial | Purpose |
|---------|---------|
| `_sidebar.html` | Role-aware sidebar nav (replaces top nav) |
| `_stat_card.html` | Reusable stat card with icon, value, trend |
| `_data_table.html` | Sortable table with pagination |
| `_empty_state.html` | Empty state with illustration + CTA |
| `_modal.html` | Confirmation modal for destructive actions |
| `_breadcrumbs.html` | Auto-generated breadcrumb trail |
| `_file_upload.html` | Drag-and-drop upload zone |
| `_toast.html` | Notification toast component |

### 4.2 Base Template Redesign

**Current → New Layout Comparison:**

```
CURRENT:                          NEW:
┌─────────────────────┐          ┌──────┬──────────────────┐
│  Top Nav Bar        │          │ Side │  Top Bar         │
├─────────────────────┤          │ bar  ├──────────────────┤
│                     │          │      │  Breadcrumbs     │
│  Content            │          │ Nav  │  Content Area    │
│  (full width)       │          │ +    │  (with padding)  │
│                     │          │ icon │                  │
│                     │          │ s    │                  │
└─────────────────────┘          └──────┴──────────────────┘
```

**Font loading (add to base.html `<head>`):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

## PHASE 5 — Per-Entity UI Rollout (Day 17-25)

### 5.1 Flow Simulation: Landing → Login → Dashboard

#### Current Flow vs. New Flow

```
CURRENT FLOW:
Landing (/) → Login (/login/) OR OTP Request (/student/verify/)
  → OTP Verify → Password → Dashboard (/dashboard/)

NEW FLOW (unchanged routes, improved UI):
Landing (/) → Unified Auth Page (/login/)
  Tab: "Staff Login" → email/password form → Dashboard
  Tab: "Student Login" → OTP email → inline code entry → Dashboard
  Link: "Forgot Password" → inline reset flow
```

**No URL changes.** Same routes, same backend logic — only template and CSS changes.

---

### 5.2 Student Entity Flow

| Page | Current State | Enhanced State |
|------|--------------|----------------|
| **Dashboard** | Flat stat cards, basic list | Sidebar nav, progress ring, calendar widget, grade sparkline, deadline countdown |
| **My Classes** | Card grid | Color-coded class cards with subject icons, enrollment status badge |
| **Class Detail** | Single long page | Tabbed interface: Stream / Assignments / Materials / Grades |
| **Assignments** | 3 lists (upcoming/overdue/complete) | Kanban columns with drag indicators, due-date color coding |
| **Submit Assignment** | Basic file input | Drag-and-drop zone, file preview, submission status timeline |
| **Grades** | Table per class | Grade cards with percentile badges, overall GPA radial chart |
| **Attendance** | Stats table | Calendar heatmap (green/yellow/red per day) |
| **Wellness Check-in** | Number inputs | Emoji sliders (😰→😊), mood history sparkline, encouraging microcopy |
| **Messages** | Basic chat | Modern chat bubbles, typing indicator, read receipts, image preview |
| **Profile** | Edit form | Card layout with avatar upload, stats summary, class enrollment list |

---

### 5.3 Teacher Entity Flow

| Page | Current State | Enhanced State |
|------|--------------|----------------|
| **Dashboard** | Stat cards + submission list | Sidebar, grading queue badge, at-risk student heatmap, submission feed |
| **My Classes** | Card grid with filter | Class cards with student count, pending grades badge, section tags |
| **Class Detail** | Long page | Tabbed: Stream / Assignments / Materials / Students / Analytics |
| **Mark Attendance** | Radio buttons per student | Batch toggle grid (Present/Late/Absent), mark-all-present button |
| **View Submissions** | Table with grade link | Split panel — submission viewer (left) + grading form (right) |
| **Grade Submission** | Separate page | Inline grading with score slider, rubric toggle, feedback textarea |
| **Students List** | Data table | Risk-colored row indicators, inline profile preview on hover |
| **Create Concern** | Form page | Quick 2-click concern from student profile (type + severity dropdowns) |

---

### 5.4 Counselor Entity Flow

| Page | Current State | Enhanced State |
|------|--------------|----------------|
| **Dashboard** | Statistics cards | Risk donut chart, alert timeline, intervention calendar, trend sparklines |
| **At-Risk Students** | Filtered table | Risk-tiered card list, sortable by score/attendance/missing, slide-out profile |
| **Alerts** | Filtered list | Severity-grouped timeline, color-coded severity bands, bulk action toolbar |
| **Interventions** | Filtered table | Timeline/Gantt view, status badges (scheduled/completed/cancelled), edit inline |
| **Create Intervention** | Form with AI recs | AI recommendations as clickable chips, auto-fill from selected recommendation |
| **Reports** | Charts + tables | Printable report builder with chart screenshots, export selector (PDF/DOCX) |
| **AI Chat** | Text input | Chat bubbles, suggested actions as chips, student search inline, typing indicator |
| **Student Profile** | Full page | Slide-out panel from any page, tabbed (Overview/Academic/Wellness/Interventions) |

---

### 5.5 Admin Entity Flow

| Page | Current State | Enhanced State |
|------|--------------|----------------|
| **Dashboard** | Statistics + activity chart | System health panel, user growth graph, risk distribution, recent activity feed |
| **Manage Users** | Filtered table | Sortable data table with inline edit/delete, role badges, bulk actions |
| **Create User** | Single form | Multi-step form (role → details → verify), auto-class creation preview |
| **Teachers List** | Simple list | Teacher cards with class count, student count, pending grades |
| **Teacher Dashboard** | Mirror of teacher view | Read-only admin overlay with audit actions |
| **Create Class** | Form | Teacher selector with profile preview, section/year auto-match preview |
| **Enroll Student** | Multi-select form | Dual-list selector (available ↔ enrolled), section/grade bulk filter |
| **Cleanup Users** | 1-click nuke | Confirmation modal with typed phrase, audit log preview, countdown timer |
| **Create Superuser** | Basic form | Password strength meter, re-authentication prompt, audit log |

---

## Regression Prevention Strategy

### Pre-Deployment Checklist (Per Phase)

| Check | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|-------|---------|---------|---------|---------|---------|
| All env vars present | ✅ | — | — | — | — |
| OTP login works | ✅ | ✅ | ✅ | ✅ | ✅ |
| Staff login works | ✅ | ✅ | ✅ | ✅ | ✅ |
| File upload works | — | ✅ | ✅ | ✅ | ✅ |
| Grading works | — | ✅ | ✅ | ✅ | ✅ |
| Admin actions work | ✅ | ✅ | ✅ | ✅ | ✅ |
| Migrations pass | — | — | ✅ | — | — |
| All templates render | — | — | — | ✅ | ✅ |
| Mobile responsive | — | — | — | ✅ | ✅ |
| Dark mode consistent | — | — | — | ✅ | ✅ |

### Rollback Plan

Each phase is independently deployable and revertible:
- **Phase 1-3:** Backend-only changes → Git revert + redeploy
- **Phase 4-5:** Template/CSS changes → Git revert, no migration needed

### Testing Script Per Phase

```bash
# Phase 1 — Security
python manage.py check --deploy          # Django deployment checklist
python manage.py test accounts           # Auth flows
curl -X GET /manage/cleanup-users/       # Should return 405 Method Not Allowed
curl -X POST /student/verify/ -d "email=test@test.com"  # 3x → rate limit

# Phase 2 — Validation
python manage.py test academics          # Grading, file upload
python manage.py test messaging          # Message send/filter

# Phase 3 — Cleanup
python manage.py makemigrations --check  # No pending migrations
python manage.py migrate --plan          # Preview migration
python manage.py test                    # Full suite

# Phase 4-5 — UI
python manage.py collectstatic --noinput # Static files build
# Manual: test each role login → dashboard → key flow
```

---

## Files Changed Summary

### New Files
| File | Purpose |
|------|---------|
| `campus_care/validators.py` | Centralized file upload validators |
| `accounts/decorators.py` | `@role_required`, `@teacher_owns_class` |
| `accounts/utils.py` | `calculate_attendance_rate`, `get_risk_counts`, `get_teacher_stats` |
| `static/css/design-system.css` | Design tokens and base styles |
| `templates/components/_sidebar.html` | Shared sidebar navigation |
| `templates/components/_stat_card.html` | Reusable stat card |
| `templates/components/_modal.html` | Confirmation modal |
| `templates/components/_empty_state.html` | Empty state |
| `templates/components/_breadcrumbs.html` | Breadcrumb trail |
| `templates/components/_file_upload.html` | Drag-drop upload |

### Modified Files
| File | Changes |
|------|---------|
| `campus_care/settings.py` | Remove defaults, add security headers, fix context processor |
| `accounts/views.py` | OTP rate limiting, password validation, email protection, logout POST |
| `accounts/admin_views.py` | POST-only destructive actions, confirmation phrases, audit logging |
| `accounts/urls.py` | Remove `/register/` and `/fix-site/` routes |
| `academics/views.py` | File validation, score validation, use decorators |
| `wellness/views.py` | Timezone fixes, error handling, AI failure logging |
| `wellness/signals.py` | Merge 3 handlers into 1 |
| `messaging/views.py` | File validation, poll endpoint fix, content filter extraction |
| `ai_assistant/views.py` | Error sanitization, prompt injection protection |
| `ml_models/gemini_client.py` | Input sanitization, SHA-256 cache keys |
| `ml_models/utils.py` | Fix `.points` → `.total_points` |
| `templates/base.html` | Sidebar layout, font loading, POST logout, SRI for CDN |
| All dashboard templates | Sidebar integration, component partials, design tokens |

### Deleted Files
| File | Reason |
|------|--------|
| `templates/base_minimal.html` | Unused |
| `templates/accounts/profile_counselor.html` | Unused |
| `messaging/content_filter.py:filter_message_content` | Dead code (function only) |
