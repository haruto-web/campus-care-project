# BrightTrack LMS - Progress Tracker

## System Overview
BrightTrack (formerly Campus Care) is an LMS with integrated student support monitoring that tracks academic performance, attendance, and wellness to identify at-risk students early.

**Live URL:** https://bright-track-project.onrender.com

---

## URL Structure

| Prefix | App |
|--------|-----|
| `/` | accounts (login, register, dashboard, profile) |
| `/class/` | academics (classes, assignments, submissions, grades, attendance) |
| `/wellness/` | wellness (check-ins, alerts, interventions, reports) |
| `/messages/` | messaging (inbox, conversations) |
| `/ai/` | ai_assistant (AI feedback) |
| `/admin/` | Django admin |
| `/accounts/` | allauth (Google OAuth) |

---

## System Workflow

### Registration & Onboarding
1. Student registers → auto-login → profile completion (pic, student number, grade level 7-10, section, phone, DOB, ID pic)
2. Teacher/Counselor created by admin → profile completion (pic, DOB, about me, or SKIP)
3. On profile completion → auto-enrolled in all classes matching section AND grade level
4. Redirected to role-based dashboard

### Teacher Workflow
1. Dashboard → view classes, at-risk students, recent submissions, quick actions
2. Create class (name, section, grade level) → matching students auto-enrolled
3. Class detail (tabbed: Assignments / Announcements / Materials / Roster)
4. Assignments → create (file/text/both submission types), view submissions with inline preview, comment (AJAX), grade with AI feedback suggestion, delete
5. Attendance → mark present/absent/late per student per day
6. Post announcements (normal/urgent), upload materials, message students/counselors
7. Submit concern for student (academic/behavioral/emotional/attendance)

### Student Workflow
1. Dashboard → stat cards (classes, pending tasks, unread announcements), upcoming assignments, recent unread announcements with read/unread toggle
2. Class detail → submit/re-submit assignments, view announcements, download materials, see roster
3. Assignments page (tabs: Upcoming / Overdue / Completed) → submit file/text/both, view score + feedback + teacher comment
4. Grades → per-class breakdown with score, percentage, feedback
5. Attendance → overall rate + per-class breakdown
6. Wellness check-in → mood/stress/sleep (emoji buttons)
7. Messaging → real-time chat, file attachments, read receipts, content filtering, student-to-student enabled
8. Notifications → receives toast + bell dropdown when intervention scheduled or teacher concern raised

### Counselor Workflow
1. Dashboard → at-risk overview, alert badge (5s polling), pending interventions, PDF/DOCX download, BT AI Assistant
2. At-Risk Students → filter by risk level, search, view full profile, schedule intervention
   - One intervention per student rule: cannot create duplicate scheduled interventions
3. Interventions → create, update status, add notes/outcome; bulk auto-create for all high-risk students
4. Alerts → filter by type/severity, mark read/resolve, view teacher concern details (expandable)
5. Reports → risk distribution, intervention stats, alert stats, academic overview (charts)
6. BT AI Assistant (/ai/counselor/) actions:
   - Create Intervention → search/filter students, select, get AI recommendations (formatted: type + success rate + reasoning), auto-creates intervention
   - Auto-Create All Interventions → creates for all high-risk students without scheduled intervention
   - Generate Report → system overview with stats
   - Analyze Behavior → attendance/submission/wellness analysis per student
   - Weekly Summary → new alerts, high-risk count, interventions, concerns this week
   - Draft Parent Email → AI-generated email draft per student
   - Search Student → filter by grade/section/severity
   - Ask AI → free-form counseling questions

### Admin Workflow
1. Dashboard → system stats, risk distribution charts, BT AI Assistant button
2. User management → add/edit/delete users, assign roles (teacher/counselor only via admin), cleanup inactive users
3. Class management → create classes for teachers, bulk enroll students (multi-select with section/grade filter)
4. Django Admin → full model-level access

### Automated Processes
1. Auto-enrollment → student completes profile or teacher creates class → matching students enrolled
2. Alert generation (Django signals) → high risk detected, 3+ missing assignments, attendance < 75%, teacher concern submitted, wellness distress
3. Notifications (5s polling) → unread message badge, bell dropdown, toast popups (new message, new announcement, assignment graded, new alert)
4. Student notifications → created when intervention scheduled or teacher concern raised; shown in bell dropdown + teal toast
5. Risk assessment → Philippine GPA system (1.00 = Excellent, 5.00 = Failing); factors: GPA, attendance, missing assignments, wellness score

---

## Data Models

### academics
- **Class** — name, code, section, year_level (7-10), teacher FK, students M2M, semester, schedule, room
- **Assignment** — class_obj FK, title, description, due_date, total_points, submission_type (file_upload/text_entry/both)
- **Submission** — assignment FK, student FK, file, text_content, score, feedback, comment, graded_at
- **Attendance** — class_obj FK, student FK, date, status (present/absent/late)
- **Announcement** — class_obj FK, author FK, title, content, priority (normal/urgent), read_by M2M
- **Material** — class_obj FK, title, file, uploaded_by FK
- **Grade** — student FK, class_obj FK, assignment FK, score, max_score

### accounts
- **User** — role (student/teacher/counselor/admin), section, year_level, student_number, profile_picture, id_picture, about_me, subject, gender, profile_completed
- **OTPCode** — contact_value (email), code, created_at, is_used

### messaging
- **Conversation** — participants M2M
- **Message** — conversation FK, sender FK, body, attachment, is_read

### wellness
- **WellnessCheckIn** — student FK, stress_level, motivation_level, workload_level, sleep_quality, need_help, text_response, date
- **RiskAssessment** — student FK, risk_level (low/medium/high), risk_score, gpa, attendance_rate, missing_assignments, date
- **Alert** — student FK, alert_type, severity, is_read, resolved
- **Intervention** — student FK, counselor FK, intervention_type, description, scheduled_date, status, notes, outcome
- **TeacherConcern** — student FK, teacher FK, concern_type, description
- **Notification** — recipient FK, notif_type (intervention_scheduled/teacher_concern), message, is_read, created_at

---

## Feature Checklist

### Teacher
- ✅ Create/edit class with section + grade level; auto-enroll matching students
- ✅ Add/remove students manually
- ✅ Tabbed class detail (Assignments / Announcements / Materials / Roster)
- ✅ Create assignment with submission type (File / Text / Both)
- ✅ Delete assignment
- ✅ Inline submission preview (text + file) before grading
- ✅ AJAX comment on submission (no page reload)
- ✅ Grade with score + feedback; AI Suggest button (Gemini)
- ✅ Mark daily attendance (present/absent/late)
- ✅ Post announcements (normal/urgent), upload/delete materials
- ✅ Submit concern (academic/behavioral/emotional/attendance)
- ✅ View student profiles (risk, GPA, attendance, wellness)

### Student
- ✅ Dashboard with unread announcement toggle (hides on check, stays in class)
- ✅ Submit/re-submit assignments (file/text/both); re-submit clears grade
- ✅ View score, teacher feedback, teacher comment (even ungraded)
- ✅ Per-class grade breakdown
- ✅ Attendance rate + per-class breakdown
- ✅ Wellness check-in (emoji buttons)
- ✅ Real-time messaging (3s polling, attachments, read receipts, content filter)
- ✅ Notifications for scheduled interventions and teacher concerns

### Counselor
- ✅ At-risk student list (filter by risk level, search, sort by score)
- ✅ One intervention per student rule (enforced at backend, view, and frontend)
- ✅ Create/update/track interventions with notes and outcomes
- ✅ Bulk auto-create interventions for all high-risk students
- ✅ Alerts with teacher concern detail toggle (expandable)
- ✅ Reports with charts (risk distribution, intervention stats, alert stats)
- ✅ PDF/DOCX report download
- ✅ BT AI Assistant (create intervention, auto-create, report, behavior analysis, weekly summary, draft email, search, ask AI)

### Admin
- ✅ Add/edit/delete users; teacher/counselor roles via admin create
- ✅ Auto-create classes when creating teacher with subject + section
- ✅ Cleanup inactive users (typed confirmation required)
- ✅ Bulk student enrollment with section/grade filter
- ✅ Dashboard stats + risk charts + PDF/DOCX download
- ✅ BT AI Assistant (/ai/admin/)
- ⚠️ Audit Log — `log_action()` helper in place, LOGIN/LOGOUT/LOGIN_FAILED logged; AuditLog model + migration + view/URL pending
- ⚠️ `admin_role` field on User pending — tier-gated sidebar links won't show until implemented

---

## Authentication
- Staff/teacher/counselor/admin → username/email + password via `/login/`
- Students → OTP email flow (`/student/verify/`) with rate limiting (3 sends/15min, 5 attempts/30min)
- Forgot password → OTP reset (`/student/forgot-password/`)
- Google OAuth (allauth)
- Role-based redirect after login

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.0, Python 3.12 |
| Database | PostgreSQL (local & Render) |
| Auth | Django Allauth (Google OAuth) |
| File Storage | Cloudinary (production), local (dev) |
| Frontend | Django Templates, Tailwind CSS, Chart.js, Vanilla JS |
| Deployment | Render (web service + PostgreSQL) |
| Static Files | WhiteNoise |
| AI | Google Gemini API |
| Email | Brevo API (transactional emails, OTP, intervention notifications) |
| Signals | Django Signals (automated alerts + notifications) |

---

## Deployment

### Render Environment Variables
```
SECRET_KEY=<your-secret-key>
DEBUG=False
DATABASE_URL=<render-postgres-url>
RENDER_EXTERNAL_HOSTNAME=bright-track-project.onrender.com
ALLOWED_HOSTS=bright-track-project.onrender.com,localhost
CLOUDINARY_CLOUD_NAME=campus-care
CLOUDINARY_API_KEY=<key>
CLOUDINARY_API_SECRET=<secret>
GOOGLE_CLIENT_ID=<id>
GOOGLE_CLIENT_SECRET=<secret>
GEMINI_API_KEY=<key>
BREVO_API_KEY=<key>
```

### build.sh
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
```

`.python-version` → `3.12.0`

---

## Known Issues

### Audit Log (Incomplete)
- `log_action()` in `accounts/utils.py` silently no-ops (AuditLog model not yet created)
- `base.html` admin sidebar references `admin_audit_log` and `admin_manage_admins` URLs → will raise `NoReverseMatch` for admin users
- Fix: implement AuditLog model + migration + views/URLs, or remove sidebar links until ready

### `admin_role` on User
- `base.html` uses `user.admin_role` for tier-gated links — field doesn't exist yet, links will never show

---

## Recent Changes

1. **Intervention notifications** — `Notification` model added; students notified (bell + toast) when intervention scheduled or teacher concern raised
2. **Intervention email** — Brevo transactional email sent to student when intervention is created with status=scheduled
3. **OTP expiry** — reduced from 10 minutes to 3 minutes
4. **One intervention per student** — enforced at backend, view level, and frontend (locked students greyed out in search)
5. **BT Assistant intervention card** — collapsible card shown after intervention created; recommendations formatted (type + success rate + reasoning)
6. **At-risk filter** — excludes non-student users from at-risk list
7. **Alert concern toggle** — teacher concern alerts show expandable detail (type, teacher, description)
8. **Admin delete user fix** — POST form submission instead of GET redirect (was causing 405)
9. **Counselor UI** — removed colored icons across all counselor templates (alerts, at-risk, interventions, reports, BT assistant)
10. **Brevo email helper** — `send_transactional_email()` in `accounts/otp_utils.py`
