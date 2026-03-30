# BrightTrack LMS

A role-based Learning Management System (LMS) with built-in student support monitoring.

BrightTrack helps schools manage classes, assignments, attendance, messaging, wellness check-ins, risk alerts, interventions, and reports in one platform.

Live site: https://bright-track-project.onrender.com

## Table of Contents
- [Core Modules](#core-modules)
- [User Roles](#user-roles)
- [Key Features](#key-features)
- [Security Highlights](#security-highlights)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Deployment (Render)](#deployment-render)
- [Main Routes](#main-routes)
- [Data Models (Summary)](#data-models-summary)
- [Testing and Validation](#testing-and-validation)
- [Roadmap](#roadmap)

<<<<<<< Updated upstream
## Core Modules
- `accounts`: authentication, OTP, profile, role access, audit logs
- `academics`: classes, attendance, assignments, submissions, materials, grades
- `wellness`: check-ins, risk assessments, alerts, interventions, reports
- `messaging`: conversations, attachments, read states, report flow
- `ai_assistant`: assistant endpoints for admin/counselor workflows
- `ml_models`: prediction and AI-related service logic
=======
| Prefix | App |
|--------|-----|
| `/` | accounts (login, register, dashboard, profile, admin management) |
| `/class/` | academics (classes, assignments, submissions, grades, attendance) |
| `/wellness/` | wellness (check-ins, alerts, interventions, reports, concerns) |
| `/messages/` | messaging (inbox, conversations, message reports) |
| `/ai/` | ai_assistant (counselor + admin AI chat) |
| `/admin/` | Django admin |
>>>>>>> Stashed changes

## User Roles
- Student
- Teacher
- Counselor
- Admin

Each role gets a dedicated dashboard and scoped permissions.

<<<<<<< Updated upstream
## Key Features
- OTP-based verification for sensitive auth flows
- Class and assignment management for teachers
- Attendance tracking and grade tracking
- Student submission and feedback flow
- Wellness check-in with risk analysis
- Alerts and intervention management
- In-app messaging with attachment support
- Audit logging for sensitive actions
- Profile management with image upload
- Activity timeline on profile (last login, recent actions, session/device info)

## Security Highlights
- Role-based access checks across major views
- OTP expiration and failed-attempt limits
- Rate limiting on sensitive endpoints
- CSRF protection and POST-only handling for destructive actions
- Audit entries with integrity hash chaining (`previous_hash`, `entry_hash`)
- Protected media serving with permission checks
- Secure cookie and HTTPS-focused production settings

## System Architecture
```mermaid
flowchart LR
    A[User Browser] --> B[Django Views and Templates]
    B --> C[(PostgreSQL)]
    B --> D[Cloudinary Media]
    B --> E[Brevo Email]
    B --> F[Gemini API]
    B --> G[Background Tasks and Signals]
=======
### Registration & Onboarding
1. Student fills registration form (student number, email, name, year level, section, password)
2. OTP sent to email → verified → `RegistrationRequest` created with status `pending`
3. Admin reviews and approves/rejects → student emailed the decision
4. On approval: User account created, `ApprovedStudent` marked `is_registered=True`
5. First login → redirected to profile completion (phone, DOB, section, year level, address, guardian info, profile pic, ID pic)
6. Profile completion can be skipped once (valid for 7 days); after expiry, forced back
7. On profile completion → auto-enrolled in all classes matching section AND grade level
8. Teacher/Counselor created by admin → profile completion (pic, DOB, about me, or SKIP)

### Teacher Workflow
1. Dashboard → view classes (with student counts), at-risk students, recent submissions grouped by class, pending grade count, section breakdowns
2. Class detail (tabbed: Assignments / Announcements / Materials / Roster)
3. Edit class (name, description, multi-block schedule, room)
4. Assignments → create (file/text/both), view submissions with inline preview, AJAX comment, grade with AI feedback suggestion, delete
5. Attendance → mark present/absent/late per student per day (also AJAX single-student update)
6. Post announcements (normal/urgent), upload/delete materials
7. Student monitoring → view all students across classes, search/filter, view full profile
8. Submit concern for student (type + severity + description + date observed)
9. Manage students → add/remove/bulk-add (filtered to matching section + grade level)

### Student Workflow
1. Dashboard → enrolled classes (with missing assignment counts), upcoming assignments, unread announcements with read/unread toggle, recently graded submissions, last wellness check-in
2. Class detail → submit/re-submit assignments, view announcements, download materials, see roster
3. Assignments page (tabs: Upcoming / Overdue / Completed) → submit file/text/both, view score + feedback + teacher comment
4. Grades → per-class breakdown with score, percentage, feedback; GPA calculation
5. Attendance → overall rate + per-class breakdown; filter by class and month
6. Wellness check-in → stress/motivation/workload/sleep (1-5 scale), need help flag, optional comments with AI sentiment analysis
7. Messaging → real-time chat (3s polling), file attachments, read receipts, content filtering, student-to-student enabled, message reporting
8. Notifications → bell dropdown + toast for intervention scheduled, teacher concern raised; real-time counts for messages, announcements, grades

### Counselor Workflow
1. Dashboard → high/medium risk counts, unread alert badge (5s polling), pending interventions, upcoming scheduled interventions, section breakdowns
2. At-Risk Students → filter by risk level/year level, search, view full profile with AI recommendations + academic pattern analysis
3. Interventions → create (one per student rule), update status, add notes/outcome; bulk auto-create for all high-risk students
4. Alerts → filter by type/severity, mark read/resolve, teacher concern detail toggle, count of students needing intervention
5. Reports → risk distribution, intervention stats, alert stats, academic overview, age range analysis (charts); PDF/DOCX download
6. Message Reports → review reported messages, apply consequences (warning/suspend/refer/no action)
7. BT AI Assistant (/ai/counselor/):
   - Create Intervention → search/select student, AI recommendations, auto-create
   - Auto-Create All Interventions → bulk for high-risk students
   - Generate Report → emoji-formatted system overview
   - Analyze Behavior → attendance/submission/wellness analysis per student
   - Weekly Summary → this week's alerts, interventions, concerns
   - Draft Parent Email → AI-generated email per student
   - Search Student → filter by grade/section/severity
   - Ask AI → scoped to BrightTrack topics only

### Admin Workflow
1. Dashboard → system stats, risk distribution, top classes, recent alerts, user activity chart, auto-risk calculation
2. User management → create teacher/counselor, view/search/filter/delete users, teachers list with class counts, teacher dashboard view
3. Student pre-approval → CSV upload or manual entry; edit/suspend approved students
4. Registration requests → approve (creates account + emails student) or reject (with reason + email)
5. Class management → create classes for teachers, view all classes, delete classes, bulk enroll students
6. Manage Admins (superadmin) → change admin_role tiers for other admins
7. System Logs (admin) → audit log with HMAC integrity verification, filtering, CSV export
8. Cleanup Users (superadmin) → mass delete non-admin users with typed confirmation
9. Create Superuser (superadmin) → create admin with Django superuser privileges
10. Messaging → lift messaging suspensions, view message reports
11. BT AI Assistant (/ai/admin/) → Generate Report, Ask AI
12. PDF/DOCX system report download
13. Django Admin → full model-level access at `/admin/`

### Automated Processes
1. Auto-enrollment → student completes profile or admin creates class → matching students enrolled
2. Alert generation (Django signals) → high/critical risk, 3+ missing assignments, attendance < 75%, teacher concern, wellness distress, emotional distress (AI), failing 3+ classes
3. Notifications (5s polling) → unread messages, announcements, grades (24h), alerts, student notifications; combined total count
4. Student notifications → created when intervention scheduled or teacher concern raised; intervention also triggers email
5. Risk assessment → Philippine GPA system; factors: GPA, attendance, missing assignments, failing classes, wellness score

---

## Data Models

### accounts
- **User** — role (student/teacher/counselor/admin), admin_role (superadmin/admin/registrar/data_viewer), section, year_level (7-10), student_number, profile_picture, id_picture, about_me, subject, gender, phone, date_of_birth, address, guardian_name, guardian_relation, guardian_occupation, profile_completed, profile_skipped_at, messaging_suspended_until
- **OTPCode** — contact_value (email), code, created_at, is_used; expires after 3 minutes
- **ApprovedStudent** — student_number (unique), email (unique), first_name, last_name, year_level, section, is_registered, is_suspended, uploaded_at
- **RegistrationRequest** — student_number, email, first_name, last_name, year_level, section, password_hash, status (pending/approved/rejected), approved_by FK, decided_at, rejection_reason; unique constraint on (student_number, email)
- **AuditLog** — actor FK, action (30+ types), target_type, target_id, target_label, extra_data (JSON), ip_address, previous_hash, entry_hash (HMAC-SHA256), signature_version, timestamp; hash-chained, non-deletable

### academics
- **Class** — name, code (unique), description, section, year_level (7-10), teacher FK, students M2M, semester, schedule (multi-block format), room, created_at
- **Assignment** — class_obj FK, title, description, due_date, total_points, submission_type (file_upload/text_entry/both), created_at
- **Submission** — assignment FK, student FK (unique_together), file, text_content, score, feedback, graded_at, submitted_at
- **Attendance** — class_obj FK, student FK, date (unique_together), status (present/absent/late), notes
- **Announcement** — class_obj FK (nullable for school-wide), author FK, title, content, priority (normal/urgent), is_school_wide, read_by M2M, created_at
- **Material** — class_obj FK, title, description, file, uploaded_by FK, uploaded_at
- **Grade** — student FK, class_obj FK, assignment FK, score, max_score, date

### messaging
- **Conversation** — participants M2M, created_at, updated_at
- **Message** — conversation FK, sender FK, body, attachment, is_read, created_at
- **MessageReport** — reporter FK, message FK, reason (harassment/inappropriate/threat/hate_speech/other), details, status (pending/reviewed/resolved/dismissed), consequence (warning/suspend/refer/no_action), counselor_notes, resolved_by FK, created_at, updated_at

### wellness
- **WellnessCheckIn** — student FK, stress_level (1-5), motivation_level (1-5), workload_level (1-5), sleep_quality (1-5), need_help, comments, text_response, date
- **RiskAssessment** — student FK, risk_level (low/medium/high/critical), risk_score, gpa, attendance_rate, missing_assignments, failing_classes, notes, date
- **Alert** — student FK, alert_type (high_risk/missing_assignments/low_attendance/wellness_concern/teacher_concern/emotional_distress/ai_intervention/failing_subjects), severity (critical/high/medium/low), message, is_read, resolved, created_at
- **Intervention** — student FK, counselor FK, intervention_type (counseling/tutoring/parent_meeting/academic_plan/other), description, scheduled_date, status (scheduled/completed/cancelled), notes, outcome, created_at, updated_at
- **TeacherConcern** — student FK, teacher FK, concern_type (academic/behavioral/emotional/attendance), severity (low/medium/high), description, date_observed, resolved, created_at
- **Notification** — recipient FK, notif_type (intervention_scheduled/teacher_concern), message, is_read, created_at

### ml_models
- **PredictionLog** — student FK, prediction_type, prediction_value (JSON), confidence, created_at
- **SentimentAnalysis** — wellness_checkin OneToOne, sentiment, confidence, alert_level, concerning_phrases (JSON), analyzed_at

---

## Feature Checklist

### Teacher
- ✅ Edit class with multi-block schedule builder; auto-enroll matching students on creation
- ✅ Add/remove/bulk-add students (filtered to matching section + grade level)
- ✅ Tabbed class detail (Assignments / Announcements / Materials / Roster)
- ✅ Create assignment with submission type (File / Text / Both); due date + points validation
- ✅ Delete assignment
- ✅ Inline submission preview (text + file) before grading
- ✅ AJAX comment on submission (no page reload)
- ✅ Grade with score + feedback; AI Suggest button (Gemini)
- ✅ Mark daily attendance (present/absent/late); AJAX single-student update
- ✅ Post announcements (normal/urgent), upload/delete materials (file type restricted)
- ✅ Submit concern with type + severity + description + date observed
- ✅ View student profiles (risk, GPA, attendance, wellness, concerns, interventions)
- ✅ Student monitoring list with search/filter by year level or class

### Student
- ✅ Dashboard with enrolled classes (missing assignment counts), unread announcement toggle, recently graded submissions
- ✅ Submit/re-submit assignments (file/text/both); re-submit clears grade
- ✅ View score, teacher feedback, teacher comment (even ungraded)
- ✅ Per-class grade breakdown with GPA calculation
- ✅ Attendance rate + per-class breakdown; filter by class and month
- ✅ Wellness check-in (1-5 scale) with AI sentiment analysis on comments
- ✅ Real-time messaging (3s polling, attachments, read receipts, content filter, message reporting)
- ✅ Notifications for scheduled interventions and teacher concerns (bell + toast + email)

### Counselor
- ✅ At-risk student list (filter by risk level/year level, search, sort by score)
- ✅ One intervention per student rule (enforced at backend + frontend)
- ✅ Create/update/track interventions with notes and outcomes; auto-resolves related alerts + concerns
- ✅ Bulk auto-create interventions for all high-risk students
- ✅ Alerts with teacher concern detail toggle (expandable); students-needing-intervention count
- ✅ Reports with charts (risk distribution, intervention stats, alert stats, age range analysis)
- ✅ PDF/DOCX report download
- ✅ Message reports review with consequences (warning/suspend/refer/no action)
- ✅ BT AI Assistant (create intervention, auto-create, report, behavior analysis, weekly summary, draft email, search, ask AI — scoped to BrightTrack topics)

### Admin
- ✅ Create teacher/counselor accounts; auto-create classes when creating teacher with subjects + sections
- ✅ Student pre-approval via CSV upload or manual entry; edit/suspend approved students
- ✅ Registration request approval/rejection with email notifications
- ✅ View/search/filter/delete users; teachers list with class counts; teacher dashboard view
- ✅ Class management: create, view all, view roster, delete classes
- ✅ Bulk student enrollment with section/grade/search filters
- ✅ Dashboard stats + risk charts + auto-risk calculation + PDF/DOCX download
- ✅ BT AI Assistant (/ai/admin/) — Generate Report, Ask AI
- ✅ Audit Log — HMAC-SHA256 hash-chained entries, integrity verification, filtering (action/actor/target/IP/date/integrity), CSV export, 50/page pagination
- ✅ `admin_role` field — superadmin/admin/registrar/data_viewer tiers; Manage Admins page (superadmin only)
- ✅ Cleanup Users (superadmin) — typed confirmation mass delete
- ✅ Create Superuser (superadmin)
- ✅ Lift messaging suspensions; view message reports

---

## Authentication & Security

### OTP Flow (all roles)
- Login: email + password → OTP sent → verify at `/verify-otp/` → logged in
- Register (students): form → OTP → verify → `RegistrationRequest` created (pending admin approval)
- Forgot password: email → OTP → verify → reset password
- OTP expires after 3 minutes
- Rate limits: 5 verify attempts/30min, 3 OTP sends/15min, 5 login attempts/10min, 5 registration attempts/10min

### Password Requirements
- Minimum 8 characters, 1 uppercase, 1 number, 1 special character
- Django CommonPasswordValidator + NumericPasswordValidator + UserAttributeSimilarityValidator

### Security Features
- HMAC-SHA256 hash-chained audit log (tamper-proof, non-deletable)
- Security notification emails: login alerts (staff), password reset/change confirmations
- CSP, HSTS, X-Frame-Options DENY, Referrer-Policy, Permissions-Policy headers
- No-cache headers on all authenticated pages
- Protected media: all files served through auth-checked endpoint with per-type authorization
- Per-endpoint rate limiting with security spike detection
- CSV injection sanitization on student uploads
- Content filtering on student messages (Filipino + English)
- Messaging suspension system with email notifications

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.0, Python 3.12 |
| Database | PostgreSQL (local & Render) |
| Auth | Django Allauth, OTP via Brevo API |
| File Storage | Cloudinary (production), local with protected media (dev) |
| Frontend | Django Templates, Tailwind CSS, Chart.js, Vanilla JS |
| Deployment | Render (web service + PostgreSQL) |
| Static Files | WhiteNoise (CompressedStaticFilesStorage) |
| AI | Google Gemini API (google-genai) |
| Email | Brevo API (OTP, notifications, security alerts, intervention emails) |
| Reports | ReportLab (PDF), python-docx (DOCX) |
| Signals | Django Signals (automated alerts + notifications) |
| Security | Custom middleware (CSP, cache control), HMAC audit chain |
| Timezone | Asia/Manila |

---

## Deployment

### Render Environment Variables
>>>>>>> Stashed changes
```

## Project Structure
```text
campus-care-project/
|- accounts/
|- academics/
|- wellness/
|- messaging/
|- ai_assistant/
|- ml_models/
|- campus_care/          # settings, urls, middleware
|- templates/
|- static/
|- manage.py
|- requirements.txt
|- build.sh
`- README.md
```

## Technology Stack
- Backend: Django 5, Python 3.12
- Database: PostgreSQL
- Frontend: Django Templates, Tailwind CSS, Vanilla JS, Chart.js
- Auth: Django auth + OTP + allauth integration
- File Storage: Cloudinary (production), local media (development)
- Email: Brevo transactional API
- AI: Gemini API integration
- Deployment: Render
- Static handling: WhiteNoise

## Local Setup
```bash
# 1) Clone
git clone https://github.com/haruto-web/campus-care-project.git
cd campus-care-project

# 2) Create virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install -r requirements.txt

# 4) Configure env
copy .env.example .env

# 5) Run migrations
python manage.py migrate

# 6) Create superuser (optional)
python manage.py createsuperuser

# 7) Start server
python manage.py runserver
```

## Environment Variables
Typical production variables:

```env
SECRET_KEY=
DEBUG=False
DATABASE_URL=
ALLOWED_HOSTS=bright-track-project.onrender.com,localhost,127.0.0.1
RENDER_EXTERNAL_HOSTNAME=bright-track-project.onrender.com
<<<<<<< Updated upstream

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

BREVO_API_KEY=
EMAIL_HOST_USER=

GEMINI_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
=======
ALLOWED_HOSTS=bright-track-project.onrender.com,localhost
CLOUDINARY_CLOUD_NAME=campus-care
CLOUDINARY_API_KEY=<key>
CLOUDINARY_API_SECRET=<secret>
GEMINI_API_KEY=<key>
BREVO_API_KEY=<key>
EMAIL_HOST_USER=<sender-email>
>>>>>>> Stashed changes
```

## Deployment (Render)
`build.sh`:
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
```

## Main Routes
- `/` - landing / authentication entry
- `/login/`, `/register/`, `/verify-otp/`, `/forgot-password/`
- `/dashboard/` - role-based dashboard redirect
- `/class/` - academics module
- `/wellness/` - wellness and interventions
- `/messages/` - messaging module
- `/ai/` - AI assistant features
- `/admin/` - Django admin

## Data Models (Summary)
- `accounts.User`: role, profile data, session key, identity fields
- `accounts.OTPCode`: OTP lifecycle and expiry
- `accounts.AuditLog`: actor, action, target, metadata, integrity hashes
- `academics.Class`, `Assignment`, `Submission`, `Attendance`, `Material`, `Announcement`, `Grade`
- `wellness.WellnessCheckIn`, `RiskAssessment`, `Alert`, `Intervention`, `TeacherConcern`
- `messaging.Conversation`, `Message`

<<<<<<< Updated upstream
## Testing and Validation
Quick checks:
```bash
python manage.py check
python manage.py test
python -m py_compile accounts\views.py
```

Manual security validation examples:
- Repeated OTP failures should trigger lockout behavior
- Unauthorized role routes should return permission denial
- Audit logs should display integrity status
- Protected media links should not be accessible without permission

## Roadmap
- Expand automated test coverage for auth and authorization flows
- Add richer observability dashboards for security events
- Improve report export options and forensic filtering
- Enhance onboarding and guided UX for each role

## License
Internal academic/capstone project (update this section if you want an open-source license).
=======
## Recent Changes

1. **Registration approval flow** — Students no longer get accounts immediately; `RegistrationRequest` model added with admin approve/reject workflow + email notifications
2. **Audit Log (fully implemented)** — `AuditLog` model with HMAC-SHA256 hash chain, integrity verification, 30+ action types, CSV export, filtering by action/actor/target/IP/date/integrity
3. **`admin_role` field (implemented)** — superadmin/admin/registrar/data_viewer tiers; Manage Admins page for superadmin; tier-gated sidebar links
4. **ApprovedStudent management** — Edit approved student details, suspend/unsuspend toggle, `is_suspended` field
5. **Message reporting system** — `MessageReport` model; users can report messages; counselors review with consequences (warning/suspend messaging/refer to admin/no action); email notifications for each consequence
6. **Messaging suspension** — `messaging_suspended_until` on User; suspended users blocked from sending; admin can lift suspensions
7. **Teacher concerns with severity** — Added severity field (low/medium/high) and resolved status to `TeacherConcern`
8. **Failing classes alert** — `failing_subjects` alert type; triggers when student fails 3+ classes
9. **Security hardening** — CSP/HSTS/cache-control middleware, protected media with per-type auth checks, rate limiting on all endpoints, security spike detection, login/password alert emails
10. **Multi-block class schedule** — Schedule builder supports multiple day/time blocks per class
11. **Admin class management** — View all classes, view class roster, delete classes
12. **Admin teacher dashboard** — View individual teacher's classes, students, at-risk count, pending grades
13. **AI scope guard** — AI assistant refuses off-topic questions; duplicate request spam blocked with cooldown
14. **Dashboard caching** — All dashboards cached for 120 seconds; reports cached for 180 seconds
15. **Bulk student management** — Bulk add students to class via checkboxes
>>>>>>> Stashed changes
