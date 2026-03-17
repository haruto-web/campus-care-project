# BrightTrack LMS — Full System Analysis

> **Date:** March 8, 2026  
> **Scope:** Security Audit, Modern LMS UI/UX Redesign Plan, Duplication & Redundancy Review  
> **System:** Django 5.0 LMS with AI-powered risk assessment (Gemini API)

---

## Table of Contents

1. [Security Vulnerability Analysis](#1-security-vulnerability-analysis)
2. [Modern LMS UI/UX Redesign Plan](#2-modern-lms-uiux-redesign-plan)
3. [Duplication & Unnecessary Code Review](#3-duplication--unnecessary-code-review)

---

## 1. Security Vulnerability Analysis

### 1.1 `campus_care/` — Project Configuration (settings.py)

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 1 | **Hardcoded default SECRET_KEY** | 🔴 CRITICAL | `settings.py:26` | The default fallback is a publicly visible insecure key. If the `.env` is missing, the app runs with a known secret that allows session hijacking, CSRF bypass, and cookie forgery. |
| 2 | **DEBUG defaults to True** | 🔴 CRITICAL | `settings.py:29` | If the env var is missing, the app runs in debug mode in production, leaking full stack traces, settings values, and SQL queries to end users. |
| 3 | **Missing security middleware headers** | 🟡 MEDIUM | `settings.py` | Absent: `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, `SECURE_BROWSER_XSS_FILTER`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS`. |
| 4 | **Duplicate context processor** | 🟢 LOW | `settings.py:89,92` | `django.template.context_processors.request` is listed twice — causes no vulnerability but indicates config sloppiness. |
| 5 | **No rate limiting on any endpoint** | 🟡 MEDIUM | `settings.py` | No `django-ratelimit` or throttle middleware. Login, OTP, and API endpoints can be brute-forced. |
| 6 | **API keys in plaintext fallback** | 🟡 MEDIUM | `settings.py:190` | `GEMINI_API_KEY` defaults to empty, but if committed in `.env`, it can leak. No rotation or vault mechanism. |

### 1.2 `accounts/` — Authentication & User Management

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 7 | **No OTP rate limiting** | 🔴 CRITICAL | `views.py:137-162` | `otp_request_view` sends OTP emails without any rate limit. Attackers can spam any email address with unlimited OTP codes, costing API credits (Brevo) and enabling email bombing. |
| 8 | **OTP brute-force possible** | 🔴 CRITICAL | `views.py:165-194` | 6-digit OTP with 10-min validity, no attempt-count lockout. An attacker can try all 1M combinations programmatically. |
| 9 | **No CSRF on logout** | 🟡 MEDIUM | `views.py:354-356` | `logout_view` processes GET requests without CSRF token. Enables logout CSRF attacks via `<img>` tags. |
| 10 | **Admin user deletion via GET-accessible endpoint** | 🟡 MEDIUM | `admin_views.py:152-173` | `admin_delete_user` does not require POST — can be triggered by link clicks or prefetching bots. |
| 11 | **Mass user deletion endpoint** | 🔴 CRITICAL | `admin_views.py:324-349` | `admin_cleanup_users` deletes ALL non-admin users in one POST. No confirmation token, no secondary auth, no audit logging. A compromised admin session can wipe the entire user base. |
| 12 | **Superuser creation via web** | 🔴 CRITICAL | `admin_views.py:351-381` | `admin_create_superuser` creates `is_superuser=True` users without password strength enforcement or 2FA. A compromised admin account can escalate privileges. |
| 13 | **Password not validated in register_view** | 🟡 MEDIUM | `views.py:79-134` | `register_view` checks length ≥ 0 only. Django's `AUTH_PASSWORD_VALIDATORS` are never called on registration input (only model validators run on save, not on `create_user`). |
| 14 | **Profile allows email change without verification** | 🟡 MEDIUM | `views.py:637-680` | `profile_view` lets users change their email directly via POST with no re-verification. This enables account takeover if combined with OTP email login. |
| 15 | **No file type validation on uploads** | 🟡 MEDIUM | `views.py:644-648` | `profile_picture` and `id_picture` accept any file type. Attackers could upload `.exe`, `.php`, or polyglot files. |
| 16 | **Authorization by string comparison** | 🟢 LOW | `admin_views.py` | Role checks use `request.user.role.lower() != 'admin'` — inconsistent with other views that use `request.user.role != 'admin'`. If role casing differs, authorization bypasses are possible. |
| 17 | **`fix_site_domain` publicly routable** | 🟡 MEDIUM | `views.py:65-77` | Modifies the Django `Site` object. Only guarded by `is_superuser`, but visible in URL config and could be discovered. |

### 1.3 `academics/` — Class & Assignment Management

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 18 | **No file type/size validation on submissions** | 🟡 MEDIUM | `views.py:562-603` | Students can upload any file type and any size. No antivirus scanning, no file extension whitelist. |
| 19 | **No file type validation on materials** | 🟡 MEDIUM | `views.py:350-369` | Teachers upload materials with no restrictions on file type or size. |
| 20 | **Destructive GET-accessible actions** | 🟡 MEDIUM | `views.py:372-382, 733-744` | `delete_material` and `delete_assignment` accept GET requests. Browser prefetchers or crawlers could trigger deletions. |
| 21 | **No IDOR protection on class access** | 🟢 LOW | `views.py:12-44` | `class_detail` allows counselors and admins to see any class (no check). This might be intentional but is not documented. |
| 22 | **Score injection** | 🟡 MEDIUM | `views.py:322-325` | `grade_submission` casts score with `int(score)` without validating range. Negative scores or scores above `total_points` are accepted. |

### 1.4 `wellness/` — Risk Assessment & Alerts

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 23 | **Bare `except: pass` hides AI failures** | 🟡 MEDIUM | `views.py:125-126` | If the Gemini API returns malformed JSON or errors, the exception is silently swallowed. Counselors never learn about failure. |
| 24 | **Reports use naive `datetime.now()`** | 🟢 LOW | `views.py:432,439` | Uses `datetime.now()` instead of `timezone.now()`, causing timezone-related bugs when `USE_TZ = True`. |
| 25 | **API endpoint exposes PII** | 🟡 MEDIUM | `views.py:528-559` | `api_students` returns full names, emails, sections, gender, and risk levels as JSON. No pagination, no rate limiting. |

### 1.5 `messaging/` — Direct Messaging

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 26 | **No file type validation on message attachments** | 🟡 MEDIUM | `views.py:45,139` | Attachments accept any file. Malicious files could be shared between users. |
| 27 | **Content filter only blocks students** | 🟢 LOW | `views.py:48-52` | `contains_inappropriate_content` only runs for `role == 'student'`. Teachers, counselors, and admins can send profanity freely. |
| 28 | **XSS in message body** | 🟡 MEDIUM | `views.py:72-80` | AJAX response returns `msg.body` without explicit HTML escaping. If rendered with `|safe` in templates, stored XSS is possible. |
| 29 | **Poll endpoint unparameterized integer cast** | 🟢 LOW | `views.py:98` | `int(request.GET.get('after', 0))` can raise `ValueError` on non-numeric input — unhandled crash. |

### 1.6 `ai_assistant/` — AI Chat Endpoints

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 30 | **Error exposure to client** | 🟡 MEDIUM | `views.py:81-85,297-298,350-351` | Stack traces and internal error messages are returned as JSON `{'error': str(e)}`. This leaks internal paths, class names, and API details. |
| 31 | **AI prompt injection via user input** | 🟡 MEDIUM | `views.py:290-292` | `action == 'ask_ai'` sends raw user message to Gemini with no sanitization. Users could craft prompts to extract system instructions or generate harmful content. |
| 32 | **Auto-created interventions without audit** | 🟡 MEDIUM | `views.py:242-288` | AI can auto-create interventions and alerts in bulk with no audit trail or approval workflow. |

### 1.7 `ml_models/` — AI/ML Integration

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 33 | **MD5 for cache keys** | 🟢 LOW | `gemini_client.py:13` | MD5 is cryptographically broken. While used only for caching (not security), SHA-256 is safer for collision avoidance. |
| 34 | **No input sanitization in AI prompts** | 🟡 MEDIUM | `gemini_client.py:39-54` | Student data (names, text) is interpolated directly into AI prompts. This enables indirect prompt injection via crafted student names or check-in text. |
| 35 | **Silent failure in `generate_text`** | 🟢 LOW | `gemini_client.py:128-129` | Returns error message containing `str(e)` to the end user. |

### 1.8 `templates/` — Frontend Security

| # | Vulnerability | Severity | File | Details |
|---|-------------|----------|------|---------|
| 36 | **Using CDN TailwindCSS (no SRI)** | 🟡 MEDIUM | `base.html:7` | `cdn.tailwindcss.com` loaded without `integrity` attribute. A CDN compromise injects JS into every page. |
| 37 | **Notification XSS via `innerHTML`** | 🟡 MEDIUM | `base.html:321-326` | `notifItems` HTML is injected via `innerHTML` from `localStorage`. If an attacker injects into localStorage (XSS), they get persistent code execution. |
| 38 | **No Content-Security-Policy header** | 🟡 MEDIUM | N/A | No CSP configured anywhere. Inline scripts run freely — any XSS becomes full exploitation. |

---

## 2. Modern LMS UI/UX Redesign Plan

The current design uses TailwindCSS CDN with Bootstrap Icons and a flat card-based layout. For a proper LMS (Learning Management System), the UI needs to follow established LMS patterns like Google Classroom, Canvas, or Moodle.

### 2.1 Current UI Problems

| Area | Problem |
|------|---------|
| **Navigation** | Top-nav only with role-based links crammed into a single bar. No sidebar. No breadcrumbs. Feels like a generic admin panel, not an LMS. |
| **Dashboard** | All four roles share the same URL and route to different views. No visual hierarchy — stat cards in a flat grid with no actionable insights. |
| **Class View** | `class_detail.html` is a single long page with all tabs (announcements, materials, assignments) on one page — no tabbed interface. |
| **Typography** | No custom fonts — relies on browser defaults through Tailwind's `font-sans`. |
| **Color System** | Generic Tailwind colors (red-600, gray-50). No branded palette. |
| **Mobile** | Hamburger menu only. No bottom navigation for students (who primarily use mobile). |
| **Dark Mode** | Implemented with basic class toggling but inconsistent across many child templates. |
| **Engagement** | No micro-animations, no loading states, no skeleton screens, no progress indicators. |
| **Empty States** | Many views show nothing when data is empty — no illustrations or guidance messages. |

### 2.2 Proposed Modern LMS Design System

#### Color Palette (BrightTrack Brand)

```
Primary:       #4F46E5 (Indigo-600)     — buttons, active states, links
Primary Dark:  #3730A3 (Indigo-800)     — hover states
Secondary:     #0EA5E9 (Sky-500)        — info, secondary actions
Success:       #10B981 (Emerald-500)    — grades, completed states  
Warning:       #F59E0B (Amber-500)      — pending, caution
Danger:        #EF4444 (Red-500)        — alerts, high risk
Surface:       #F8FAFC (Slate-50)       — page background
Surface Dark:  #0F172A (Slate-900)      — dark mode background
Card:          #FFFFFF                   — card backgrounds
Card Dark:     #1E293B (Slate-800)      — dark mode cards
```

#### Typography

```
Headings:      Inter (Google Fonts), 600-700 weight
Body:          Inter, 400 weight
Monospace:     JetBrains Mono (for grades/codes)
```

### 2.3 Layout Redesign by Role

#### A. Student View — "My Learning Hub"

**Layout:** Collapsible sidebar (desktop) + Bottom Tab Bar (mobile)

```
┌────────────────────────────────────────────────────────┐
│ [Logo]        Search...          🔔  💬  👤  🌙       │
├──────────┬─────────────────────────────────────────────┤
│          │                                             │
│ 📊 Dash  │  Welcome back, Juan!                       │
│ 📚 Class │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ 📝 Tasks │  │ GPA: 3.2 │ │ 95% Att  │ │ 2 Pending│   │
│ 📈 Grades│  └──────────┘ └──────────┘ └──────────┘   │
│ ❤️ Well  │                                             │
│ 💬 Chat  │  Upcoming Deadlines         Recent Grades  │
│          │  ┌──────────────────┐      ┌──────────────┐│
│ ─────── │  │ Math HW - Mar 10 │      │ 92/100  A    ││
│ ⚙️ Sets  │  │ Sci Lab - Mar 12 │      │ 88/100  B+   ││
│          │  └──────────────────┘      └──────────────┘│
└──────────┴─────────────────────────────────────────────┘
```

**Key features:**
- Progress ring showing overall completion percentage
- Calendar widget for deadlines
- Wellness mood tracker as a floating widget
- Grade trend sparkline chart
- Class cards with color-coded subject tags

#### B. Teacher View — "Teaching Dashboard"

**Layout:** Fixed sidebar + Content area with tabs

```
┌────────────────────────────────────────────────────────┐
│ [Logo]        Search Students...  🔔  💬  👤          │
├──────────┬─────────────────────────────────────────────┤
│          │                                             │
│ 📊 Over  │  Quick Stats                               │
│ 📚 Class │  ┌────────┐ ┌────────┐ ┌────────┐         │
│ 👥 Studs │  │48 Studs│ │12 Grade│ │ 3 Risk │         │
│ 📋 Grade │  └────────┘ └────────┘ └────────┘         │
│ ⚠️ Concrn│                                             │
│ 💬 Chat  │  Classes          │ Submissions Feed       │
│          │  ┌───────────┐    │ ┌───────────────────┐  │
│          │  │ Math G7-A │    │ │ Juan - HW3  ✅    │  │
│          │  │ 24 studs  │    │ │ Maria - HW3  ⏳   │  │
│          │  │ 3 pending │    │ │ Pedro - Lab2 ✅    │  │
│          │  └───────────┘    │ └───────────────────┘  │
└──────────┴─────────────────────────────────────────────┘
```

**Key Features:**
- Kanban-style grading queue (ungraded → reviewing → graded)
- Inline grading with rubric support
- Batch attendance marking with swipe gestures (mobile)
- Student risk heatmap per class
- Quick-concern reporting with 2-click flow

#### C. Counselor View — "Student Wellness Center"

**Layout:** Fixed sidebar + Split-panel detail view

```
┌────────────────────────────────────────────────────────┐
│ [Logo]        Search Students...   🔔  🤖  👤         │
├──────────┬─────────────────────────────────────────────┤
│          │                                             │
│ 📊 Dash  │  Risk Overview          Active Alerts (5)  │
│ ⚠️ Alerts│  ┌──────────────┐      ┌────────────────┐  │
│ 👥 Risk  │  │  🔴 8 High   │      │ Juan - Absent  │  │
│ 📋 Inter │  │  🟡 15 Med   │      │ Maria - Stress │  │
│ 📊 Report│  │  🟢 42 Low   │      │ Pedro - Grades │  │
│ 🤖 AI    │  └──────────────┘      └────────────────┘  │
│ 💬 Chat  │                                             │
│          │  Student Profile (click any alert)          │
│          │  ┌──────────────────────────────────────┐   │
│          │  │ [Photo] Juan Cruz   G7 - Section A   │   │
│          │  │ Risk: HIGH  │ GPA: 1.8 │ Att: 65%   │   │
│          │  │ AI Recommendation: Tutoring + Counsel│   │
│          │  └──────────────────────────────────────┘   │
└──────────┴─────────────────────────────────────────────┘
```

**Key features:**
- Risk dashboard with donut chart + trend sparklines
- Student profile as slide-out panel (no page reload)
- AI chatbot accessible as floating button
- Intervention timeline (visual Gantt-like view)
- Alert severity color-coding with auto-sort

#### D. Admin View — "System Administration"

**Layout:** Sidebar + Data table-heavy content

```
┌────────────────────────────────────────────────────────┐
│ [Logo]          System Admin        🔔  🤖  👤        │
├──────────┬─────────────────────────────────────────────┤
│          │                                             │
│ 📊 Dash  │  System Stats                              │
│ 👥 Users │  ┌────────┐ ┌────────┐ ┌────────┐         │
│ 📚 Class │  │156 User│ │12 Teach│ │ 24 Cls │         │
│ 📋 Enrol │  └────────┘ └────────┘ └────────┘         │
│ 📊 Report│                                             │
│ 🤖 AI    │  User Management                           │
│ ⚙️ Setts │  ┌──────────────────────────────────────┐   │
│          │  │ Filter: [Role ▾] [Section ▾] [Search]│   │
│          │  │ ┌──────────────────────────────────┐ │   │
│          │  │ │ Name  │ Role  │ Section │ Action │ │   │
│          │  │ │ Cruz  │ Stud  │ G7-A    │ ✏️ 🗑️  │ │   │
│          │  │ └──────────────────────────────────┘ │   │
│          │  └──────────────────────────────────────┘   │
└──────────┴─────────────────────────────────────────────┘
```

### 2.4 Component Redesign Specifications

#### Navigation (All Roles)
- **Desktop:** Fixed left sidebar (240px collapsed / 64px icon-only mode) with icons + labels
- **Mobile:** Bottom tab bar (5 icons) for primary nav + hamburger for secondary
- **Breadcrumbs:** Auto-generated from URL path on all inner pages
- **Active state:** Indigo left-border (4px) + filled background

#### Cards & Data Display
- **Stat cards:** Rounded-2xl, subtle shadow, icon on left, number prominent, trend indicator (↑/↓ with color)
- **Data tables:** Striped rows, sticky headers, inline actions, row hover highlight
- **Empty states:** SVG illustration + descriptive text + CTA button
- **Loading:** Skeleton screens for all data-fetching views

#### Forms
- **Input fields:** Floating labels, focus ring in primary color, validation messages inline
- **Buttons:** Primary (indigo fill), Secondary (outline), Danger (red), sizes: sm/md/lg
- **File uploads:** Drag-and-drop zone with preview
- **Multi-step:** Stepper indicator for registration and profile completion

#### Feedback & Notifications
- **Toast notifications:** Slide-in from bottom-right, auto-dismiss in 5s, color-coded
- **Alert banners:** Full-width, dismissible, with action buttons
- **Modal confirmations:** For all destructive actions (delete, drop, cleanup)
- **Loading spinners:** Branded indigo spinner for all async operations

### 2.5 Key Pages to Redesign

| Page | Current Issue | Proposed Fix |
|------|---------------|--------------|
| Landing page | Basic hero section | Animated hero with feature showcase, testimonials section, role-specific CTA buttons |
| Login/Register | Separate pages, plain forms | Single-page auth with tab switch (Login/Register), social login prominent, OTP flow as inline steps |
| Student Dashboard | Flat stat cards | Progress dashboard with radial charts, calendar widget, deadline countdown, grade trend graph |
| Class Detail | Long single page | Tabbed interface (Stream / Assignments / Materials / Students / Grades) — Google Classroom style |
| Grading View | Basic table | Split-panel: submission viewer on left, grading form on right, inline rubric |
| Wellness Check-in | Basic form | Animated emoji slider, mood calendar heatmap, encouraging copy |
| Counselor Alerts | Simple list | Severity-sorted timeline with color-coded cards and quick-action buttons |
| AI Chat | Plain text interface | Modern chat bubbles, typing indicator, suggested actions as chips |

---

## 3. Duplication & Unnecessary Code Review

### 3.1 `accounts/` — Authentication & User Management

| # | Type | Location | Details |
|---|------|----------|---------|
| 1 | **Duplicate registration flow** | `views.py:79-134` + `views.py:283-327` | `register_view` (L79) and `otp_register_view` (L283) both create student users with nearly identical logic. Only `register_view` sets `year_level` and `gender` before save. Consolidate into one helper. |
| 2 | **Duplicate dashboard logic** | `views.py:425-508` + `admin_views.py:190-229` | `teacher_dashboard` in views.py and `admin_teacher_dashboard` in admin_views.py duplicate student collection, risk assessment filtering, and pending grade counting. Extract a shared `get_teacher_stats(teacher)` utility. |
| 3 | **Duplicate attendance rate calculation** | `views.py:668-672`, `views.py:705-709`, `views.py:798-803` | The pattern `(present_count / total_count) * 100` is repeated 3 times in different views. Create a `calculate_attendance_rate(student)` utility function. |
| 4 | **Duplicate `from collections import defaultdict`** | `views.py:453,467,532` | Imported inside function bodies 3 times. Move to top-level imports. |
| 5 | **Unused `register_view`** | `views.py:79-134` | Students use the OTP flow. The old registration view appears unused but is still routed at `/register/`. Either remove or document. |
| 6 | **`fix_site_domain` utility view** | `views.py:65-77` | A one-time setup helper that should be a management command, not a web-accessible view. |

### 3.2 `academics/` — Class & Assignment Management

| # | Type | Location | Details |
|---|------|----------|---------|
| 7 | **Duplicate permission checks** | `views.py` (throughout) | Every teacher view repeats `if request.user.role != 'teacher' or class_obj.teacher != request.user`. Create a `@teacher_owns_class` decorator or mixin. |
| 8 | **Duplicate student role checks** | `views.py:421,471,506,541,606,671` | `if request.user.role != 'student'` repeated 6 times. Create a `@role_required('student')` decorator. |
| 9 | **`Grade` model appears unused** | `models.py:80-89` | The `Grade` model is defined but only referenced in `drop_student` for deletion. All actual grading goes through `Submission.score`. This model is redundant. |
| 10 | **`announcement_views.py` separate file** | `announcement_views.py` | Contains only 2 small view functions. These should be in the main `views.py` file to reduce module fragmentation. |
| 11 | **Duplicate class filtering in views** | `views.py:384-415` | `my_classes` applies `year_level_filter` by filtering students in classes, which is semantically odd. This filter logic is fragile and duplicated. |

### 3.3 `wellness/` — Risk Assessment & Wellness

| # | Type | Location | Details |
|---|------|----------|---------|
| 12 | **Duplicate risk count queries** | `views.py:359-361` + `views.py:492-498` + `accounts/views.py:593-595` | `RiskAssessment.objects.filter(risk_level='high').count()` is repeated in `reports_view`, `generate_report`, and `admin_dashboard`. Create a `RiskAssessment.get_counts()` class method. |
| 13 | **Duplicate report generation** | `views.py:482-526` + `accounts/report_views.py:6-27` | `generate_report` in wellness and `get_report_data` in accounts both query the same risk/alert/intervention data for report generation. The report logic is split across two apps unnecessarily. |
| 14 | **Five signal handlers for one model** | `signals.py` | Three separate `@receiver(post_save, sender=RiskAssessment)` handlers. These should be combined into one handler that checks all conditions — saves 2 database save hooks. |
| 15 | **Duplicate `JsonResponse` import** | `views.py:532,535` | `from django.http import JsonResponse` imported twice in `api_students`. |
| 16 | **`WellnessCheckIn.comments` and `text_response`** | `models.py:12-13` | Two text fields for essentially the same data. `comments` is blank=True, `text_response` is also blank+null. Only `text_response` is used in views. `comments` is never referenced. |

### 3.4 `messaging/` — Direct Messaging

| # | Type | Location | Details |
|---|------|----------|---------|
| 17 | **Duplicate content filter check** | `views.py:48-52` + `views.py:147-158` | Inappropriate content check is duplicated between `conversation` (sending in existing thread) and `new_message` (starting new thread). Extract to a shared helper or middleware. |
| 18 | **Duplicate message creation with fallback** | `views.py:55-68` + `views.py:166-172` | Try/except pattern for creating messages with/without attachment is copy-pasted. Create a `create_message_safely()` utility. |
| 19 | **`filter_message_content` unused** | `content_filter.py:51-69` | Imported in `views.py` but never called. The system blocks messages entirely instead of filtering. Dead code. |

### 3.5 `ai_assistant/` — AI Chat

| # | Type | Location | Details |
|---|------|----------|---------|
| 20 | **Duplicate report generation logic** | `views.py:87-114` + `views.py:314-341` | `counselor_chat` and `admin_chat` both have `'generate_report'` action with near-identical data gathering and prompt construction. Extract to a shared function. |
| 21 | **Duplicate `'ask_ai'` handler** | `views.py:290-292` + `views.py:343-345` | Both chat views have identical `action == 'ask_ai'` handlers. |
| 22 | **Duplicate auto-intervention logic** | `views.py:242-288` + `wellness/views.py:271-318` | Auto-creating interventions for high-risk students is implemented in both `ai_assistant` (via AI chat) and `wellness` (via bulk button). |

### 3.6 `ml_models/` — AI/ML Integration

| # | Type | Location | Details |
|---|------|----------|---------|
| 23 | **`utils.py` attendance calculation duplicates `accounts/views.py`** | `utils.py:12-19` | The 30-day attendance rate calculation in `get_student_data_for_prediction` duplicates the pattern used in multiple places in `accounts/views.py`. |
| 24 | **`Assignment.total_points` vs `Assignment.points`** | `utils.py:98` | References `sub.assignment.points` but model field is `sub.assignment.total_points`. This would cause an `AttributeError` at runtime — dead or broken code. |

### 3.7 `templates/` — Frontend

| # | Type | Location | Details |
|---|------|----------|---------|
| 25 | **Duplicate navigation in desktop + mobile** | `base.html:31-48` + `base.html:132-178` | All navigation items are duplicated for desktop (inline) and mobile (hamburger menu). Should use a single template partial with responsive CSS. |
| 26 | **Duplicate quick actions** | `base.html:85-110` + `base.html:151-166` | Quick action links for student and teacher are duplicated between dropdown and mobile menu. |
| 27 | **Multiple unused templates** | Various | `base_minimal.html` (729 bytes) does not appear to be extended by any template. `profile_counselor.html` exists but `profile_view` routes counselors to `accounts/profile.html`, not `profile_counselor.html`. |
| 28 | **Inline CSS/JS in every template** | All templates | Each template embeds its own `<style>` blocks with Tailwind classes. No shared component library or CSS file (only a 3.6KB `custom.css`). |

### 3.8 Cross-Module Issues

| # | Type | Details |
|---|------|---------|
| 29 | **Empty test files** | `academics/tests.py`, `accounts/tests.py`, `messaging/tests.py`, `wellness/tests.py` — all contain only `from django.test import TestCase` with no actual tests. Zero test coverage. |
| 30 | **`WORKSPACE_ANALYSIS.md` and `PRESENTATION.md`** | Large markdown files (22KB and 8KB) that appear to be one-time documents. Should be in a `docs/` folder, not project root. |
| 31 | **`setup_google_oauth.py` in project root** | A one-time setup script. Should be a management command or in a `scripts/` directory. |
| 32 | **`messaging` not in INSTALLED_APPS order** | `settings.py:64` — messaging is listed after cloudinary packages. Should be grouped with project apps. |

---

## Summary of Findings

### Security — Priority Matrix

| Priority | Count | Key Actions |
|----------|-------|-------------|
| 🔴 CRITICAL | 6 | Remove default SECRET_KEY, set DEBUG=False default, add OTP rate limiting, add brute-force protection, require CSRF/POST for destructive actions, protect mass deletion |
| 🟡 MEDIUM | 20 | Add security headers, validate file uploads, sanitize AI prompts, add CSP, rate-limit endpoints, validate scores |
| 🟢 LOW | 8 | Fix timezone usage, remove dead code, standardize role checks |

### UI/UX — Core Changes Needed

1. **Add persistent sidebar navigation** (replace top-nav-only)
2. **Implement tabbed class view** (Google Classroom style)
3. **Add custom brand fonts** (Inter from Google Fonts)
4. **Create a design token system** (colors, spacing, shadows)
5. **Add micro-interactions** (loading states, transitions, skeleton screens)
6. **Build mobile bottom tab bar** for students
7. **Add empty state illustrations** for all list views
8. **Modernize forms** with floating labels and drag-and-drop upload

### Duplication — Remediation Summary

1. Create **shared decorator** for role/permission checks (`@role_required`, `@teacher_owns_class`)
2. Extract **utility functions** for attendance rate, risk counts, student data collection
3. Merge **duplicate registration flows** into a single service function
4. Consolidate **report generation** into one app (`reports/`)
5. Remove **dead code**: `Grade` model, `filter_message_content`, unused templates, `register_view`
6. Create **template partials** for navigation, stat cards, and form components
7. Combine **signal handlers** for `RiskAssessment` into one function
