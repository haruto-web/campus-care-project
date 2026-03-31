# BrightTrack LMS — Role Logic Reference

---

## Student

### Registration & Login
- Students register via **student number + email + first name + last name + year level + section + password** form at `/register/`
- Student number must be exactly **12 digits**
- Year level must be 7, 8, 9, or 10
- Password validated by Django validators + `StrongPasswordValidator` (1 uppercase, 1 number, 1 special character)
- Registration rate limit: 5 attempts per IP per 10 minutes
- After form submission, OTP is sent to email → verify at `/verify-otp/`
- On OTP verification, a `RegistrationRequest` is created with status `pending` — **account is NOT created yet**
- Admin must approve or reject the registration request; student is emailed the decision
- On approval: User account is created, `ApprovedStudent` record marked `is_registered=True`
- On rejection: reason is stored and emailed to student; no account created
- All roles use the same `/login/` page (email + password) → OTP sent → verify → logged in
- Login rate limit: 5 attempts per IP+email per 10 minutes
- OTP rate limits: 5 verify attempts per email per 30 minutes; 3 OTP sends per email per 15 minutes
- OTP expires after **3 minutes**
- Forgot password uses OTP flow at `/forgot-password/` → verify → reset at `/reset-password/`
- Password reset and login trigger security notification emails to the user
- Staff/teacher/counselor/admin login triggers a "New Login Alert" email with timestamp and IP
- After registration approval + first login, redirected to **profile completion**
- Profile completion fields: phone, DOB, section, year level, address, guardian name/relation/occupation, profile pic, ID pic
- Profile completion can be **skipped once** — skip is valid for 7 days
- After 7-day skip expires, `profile_completed` is reset to False and student is redirected on next dashboard load

### Auto-Enrollment
- When a student completes their profile with a **section + grade level**, they are automatically enrolled in all classes matching **both** values
- Example: Grade 7, Section Apple → enrolled in all "Grade 7 Apple" classes

### Dashboard
- Shows: enrolled classes (with missing assignment count per class), upcoming assignments (due soonest, max 5), unread announcements (max 6 with read/unread status), recently graded submissions (last 5), last wellness check-in, total missing assignments count
- Announcements can be toggled read/unread via AJAX — read ones are hidden from dashboard but still visible inside the class
- Dashboard is cached for 120 seconds per student

### Classes
- Can view all enrolled classes
- Inside a class: view assignments (with submission status), announcements, materials, and roster (read-only)

### Assignments
- Three tabs: **Upcoming** (not submitted, not overdue), **Overdue** (not submitted, past due), **Completed** (submitted)
- Submission types depend on what the teacher set: file upload, text entry, or both
- Can re-submit — this clears the previous score, feedback, and graded_at
- Completed tab shows: score (e.g. 8/10), teacher feedback, and teacher comment (even if not yet graded)
- Submission rate limit: 10 attempts per assignment per 10 minutes

### Grades
- Per-class breakdown of all graded assignments
- Shows score, percentage, and feedback/comment per assignment
- Can filter by class
- GPA calculated as (total_score / total_points × 4.0)

### Attendance
- View overall attendance rate (present/late/absent counts)
- Per-class breakdown with individual records
- Can filter by class and by month (current/last)

### Wellness Check-In
- Submit mood check-in: stress level (1-5), motivation (1-5), workload (1-5), sleep quality (1-5), need help flag, and optional comments
- If comments are provided, Gemini AI performs sentiment analysis; if alert level is high/critical, a high-severity `emotional_distress` alert is auto-created
- If stress ≥ 4, motivation ≤ 2, or need_help is true, a `wellness_concern` alert is auto-created via Django signal
- Can view last 5 check-in history

### Messaging
- Can message teachers, counselors, and other students
- Real-time chat via 3-second polling
- File/image attachments supported (validated via `validate_document_upload`)
- Content filtering active (Filipino & English profanity) — only applied to student messages
- Read receipts shown (Messenger-style "Read" under last read sent message)
- Can report messages (harassment, inappropriate, threat, hate speech, other)
- Messaging can be suspended by counselor/admin — suspended users see expiry date and cannot send
- Message send rate limit: 30 per conversation per 5 minutes; new message: 20 per 5 minutes

### Notifications
- Bell dropdown + toast popups for: intervention scheduled, teacher concern raised
- Notifications stored in `Notification` model, polled every 5 seconds
- Can mark all notifications as read via AJAX
- Also receives real-time counts for: unread messages, unread announcements, recently graded submissions (last 24h)

---

## Teacher

### Login
- Uses **email + password** → OTP verification (same flow as all roles)
- Login triggers security notification email

### Dashboard
- Shows: classes taught (with student counts), at-risk students (high risk only), pending grade count, recent submissions grouped by class (max 3 per class, 15 total)
- Section-based breakdowns: students by section, at-risk by section, pending grades by section
- Dashboard is cached for 120 seconds per teacher

### Class Management
- Create class is disabled for teachers directly — redirects to admin
- Edit class: name, description, schedule (multi-block schedule builder with day/time), room
- On class creation (by admin), students with matching section AND grade level are auto-enrolled
- Tabbed class detail: Assignments / Announcements / Materials / Roster

### Student Management
- Add/remove students from a class
- Only students matching the class section AND grade level are shown as available
- Bulk add multiple students at once via checkboxes
- Dropping a student removes all their grades, attendance, and submissions for that class

### Assignments
- Create with: title, description, due date (must be in future), total points (1-100), submission type (file / text / both)
- Creation rate limit: 15 per class per 10 minutes
- Delete assignment (POST only)
- View all submissions for an assignment — filter by graded/pending
- Inline preview: expand a submission row to see text content + file before grading
- Leave a comment on a submission via AJAX (no page reload, updates feedback field)
- Grade submission: enter score (0 to total_points) + feedback, with optional AI-suggested feedback (Gemini)
- Student is notified when graded (via polling — submissions graded in last 24h)

### Attendance
- Mark each student as Present / Absent / Late for today
- Updates existing record if already marked (`update_or_create`)
- Also supports AJAX single-student attendance update
- Attendance marking is audit-logged

### Announcements & Materials
- Post announcements with Normal or Urgent priority
- Upload class materials (files with title and description)
- Material file types restricted to: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, ZIP, CSV
- Material upload rate limit: 15 per class per 10 minutes
- Delete materials (POST only)

### Student Monitoring
- View list of all students across teacher's classes — search by name/email, filter by year level or class
- Students sorted by risk level (high first)
- View individual student profile: risk level, GPA, attendance rate, wellness check-ins, concerns, interventions
- Submit a concern about a student: type (Academic / Behavioral / Emotional / Attendance), severity (Low / Medium / High), description, date observed
- Can only submit concerns for students in their own classes
- Concern submission rate limit: 10 per 10 minutes

### Messaging
- Can message counselors, admins, and students
- Same real-time chat features as students

---

## Counselor

### Login
- Uses **email + password** → OTP verification (same flow as all roles)

### Dashboard
- Shows: high/medium risk student counts, unread alert count, pending interventions, upcoming scheduled interventions (next 5)
- Section-based breakdown of high and medium risk students
- Quick Actions: Download PDF report, Download DOCX report, BT AI Assistant
- Dashboard is cached for 120 seconds

### At-Risk Students
- View all students with risk assessments (filtered to role=student only), sorted by risk score
- Filter by risk level (High / Medium / Low), search by name/email, filter by year level
- Click a student to view full profile: risk score, GPA, attendance, wellness history, concerns, interventions, AI prediction
- AI intervention recommendations shown on profile if student is medium/high risk (Gemini)
- Academic pattern analysis also shown (Gemini) — only if student has assignment score data

### Interventions
- Create intervention for a student: type (counseling/tutoring/parent_meeting/academic_plan/other), description, scheduled date
- **One intervention per student rule**: cannot create if student already has a scheduled intervention (enforced at backend)
- When created: related critical/high alerts for that student are auto-resolved; teacher concerns are marked resolved
- Student receives notification (bell + toast) and email when intervention is scheduled
- Update intervention: change status (Scheduled → Completed / Cancelled), add notes, update outcome
- Filter by status (Scheduled / Completed / Cancelled / History) and year level
- Bulk auto-create: creates interventions for all students with unresolved critical/high alerts who don't already have a scheduled one; auto-resolves those alerts
- Intervention creation rate limit: 10 per 10 minutes

### Alerts
- View all unresolved alerts, color-coded by severity (critical/high/medium/low)
- Filter by type, severity, show resolved toggle
- Mark individual alert as read
- Resolve individual alert
- Shows count of students with critical/high alerts who lack a scheduled intervention
- Teacher concern alerts show expandable detail (concern type, teacher name, description)
- Alerts are auto-generated by Django signals (see Automated Processes below)

### Reports
- Risk level distribution (High / Medium / Low counts)
- Intervention statistics (scheduled, completed, cancelled, completion rate) + by type breakdown
- Alert statistics (unresolved, resolved, resolution rate) + by type breakdown
- Academic overview (average attendance rate, total concerns, total check-ins)
- Age range analysis of high-risk students (15-17, 18-20, 21-23, 24+) with most problematic range
- Recent concerns (last 7 days) and upcoming interventions
- Charts: risk distribution pie, intervention status pie, age range bar
- Download as PDF or DOCX
- Report data cached for 180 seconds
- Report generation rate limit: 10 per 10 minutes

### Message Reports
- View all message reports filed by users
- Filter by status (pending/reviewed/resolved/dismissed)
- Resolve reports with consequence: Warning (email sent), Suspend Messaging (1 week, email sent), Refer to Admin (email sent), No Action
- Messaging suspension sets `messaging_suspended_until` on the reported user

### BT AI Assistant (`/ai/counselor/`)
- **Create Intervention** — search/select student, get AI recommendations (type + success rate + reasoning), auto-creates intervention with 3-day schedule
- **Auto-Create All Interventions** — creates for all high-risk students without scheduled intervention; creates AI alert for each
- **Generate Report** — system overview with emoji-formatted stats (4 sections)
- **Analyze Behavior** — attendance/submission/wellness analysis per student (last 30 attendance, 20 submissions, 10 check-ins)
- **Weekly Summary** — new alerts, high-risk count, interventions, concerns this week
- **Draft Parent Email** — AI-generated email draft per student with risk context and recent concerns
- **Search Student** — filter by grade/section/severity
- **Ask AI** — free-form questions, but **scoped to BrightTrack topics only** (off-topic requests are refused)
- All AI actions are rate-limited per action type; duplicate request spam is blocked (20s cooldown per identical request)
- All AI usage is audit-logged

### Messaging
- Can message admins, other counselors, teachers, and students

---

## Admin

### Login
- Uses **email + password** → OTP verification (same flow as all roles)

### Admin Roles (tier-gated sidebar)
- `superadmin` — full access: Create Superuser, System Logs, Manage Admins, Cleanup Users, all lower tiers
- `admin` — Create Class, Create User, Enroll Students, Upload Students
- `registrar` — Enroll Students, Upload Students only
- `data_viewer` — read-only access tier

### Dashboard
- System stats: total users, students, teachers, counselors, admins, classes, assignments
- Risk distribution: high/medium/low risk counts (deduplicated by student)
- Top 5 classes by enrollment
- Recent alerts (last 5)
- Unresolved alerts count, pending interventions count
- User activity chart (last 30 days, 5-day intervals)
- Auto-runs risk calculation (`calculate_risk`) on load if assessments are stale (older than today); runs in background thread with lock to prevent concurrent runs
- Download PDF / DOCX system report
- BT AI Assistant button
- Dashboard is cached for 120 seconds

### User Management
- Create teacher or counselor accounts (students self-register via approved list + admin approval)
- When creating a teacher with subjects + sections + grade level, classes are auto-created for each subject-section combination (code format: `G{year_level}-{section}-{subject[:3].upper()}`)
- View/search/filter all users by role, name, year level, section
- Delete users (POST only, cannot delete admin accounts)
- Teachers redirect to teachers list after deletion; others redirect to manage users
- View teachers list with class counts
- View individual teacher dashboard (classes, at-risk students, pending grades)

### Student Pre-Approval
- Upload CSV to pre-approve students for registration (`ApprovedStudent` table)
- CSV columns: `student_number` (12 digits), `email`, `first_name`, `last_name`, `year_level` (7–10), `section` (optional)
- CSV max size: 5MB; CSV injection sanitization applied (strips leading `=`, `+`, `-`, `@`)
- Or add students manually one at a time via the "Add Manually" tab
- `update_or_create` logic — re-uploading updates existing records
- Edit approved student details inline
- Suspend/unsuspend approved students (`is_suspended` toggle)
- Registered students are marked `is_registered=True`

### Registration Requests
- View pending registration requests (tab on Upload Students page)
- Approve: creates User account atomically with `select_for_update()`, creates/updates `ApprovedStudent`, sends approval email
- Reject: stores reason, sends rejection email; no account created
- Duplicate email check on approval — blocks if email already exists in active users

### Class Management
- Create classes and assign to any teacher
- View all classes with student counts, sorted by year level/section/name
- View individual class roster
- Delete classes (POST only)
- Enroll students into classes manually — multi-select with section/grade/search filters; shows recent enrollments

### Manage Admins (`/manage/admins/`) — superadmin only
- View all admin users
- Change admin_role (superadmin/admin/registrar/data_viewer) for other admins
- Cannot change own admin role
- Role changes are audit-logged with old/new role

### System Logs (`/manage/audit-log/`) — admin required
- View all audit log entries with HMAC-SHA256 integrity verification
- Filter by: action type, actor name, target (label/type/ID), IP address, integrity status (unaltered/not verified), date range
- Paginated (50 per page)
- Export to CSV with all fields including integrity status
- Export action is itself audit-logged
- Audit log entries cannot be deleted through application code (`PermissionError` raised)
- Each entry is hash-chained to the previous entry for tamper detection

### Cleanup Users (`/manage/cleanup-users/`) — superadmin only
- Deletes all non-admin users at once
- Requires typing "DELETE ALL USERS" exactly to confirm
- Mass deletion is audit-logged with counts

### Create Superuser (`/manage/create-superuser/`) — superadmin only
- Creates admin user with `is_staff=True`, `is_superuser=True`
- Password validated by Django validators

### Messaging Suspension
- Lift messaging suspension for any user (`/manage/user/<id>/lift-suspension/`)
- Sends email notification to user when suspension is lifted

### BT AI Assistant (`/ai/admin/`)
- **Generate Report** — executive summary with system stats
- **Ask AI** — free-form questions, scoped to BrightTrack topics only
- Rate-limited per action type

### Django Admin
- Full model-level access at `/admin/`

---

## Authentication & Security

### OTP Flow (all roles)
- Login: credentials verified → OTP sent to email → verify at `/verify-otp/` → logged in
- Register (students): form submitted → OTP sent → verify → `RegistrationRequest` created (pending admin approval)
- Forgot password: email entered → OTP sent → verify → reset password at `/reset-password/`
- OTP expires after 3 minutes
- OTP rate limits: 5 verify attempts per email per 30 minutes; 3 OTP sends per email per 15 minutes
- Registration rate limit: 5 attempts per IP per 10 minutes
- Login rate limit: 5 attempts per IP+email per 10 minutes
- Registration data (password hash) stored server-side in Django session between form and OTP step; cleared after request creation

### Password Requirements (`StrongPasswordValidator`)
- Minimum 8 characters (Django default)
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character
- Not too common (Django `CommonPasswordValidator`)

### Security Emails
- Login alert email sent to staff/teacher/counselor/admin on successful login (includes timestamp + IP)
- Password reset request notification email
- Password changed confirmation email (includes timestamp + IP)

### Security Headers (Middleware)
- Authenticated pages: `Cache-Control: no-cache, no-store, must-revalidate, private`
- Content-Security-Policy: restricts scripts, styles, fonts, images, connections, frames
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

### Protected Media
- All media files (profiles, ID pictures, materials, submissions, message attachments) served through `/media/<path>` with authentication and authorization checks
- Profile pictures: any authenticated user
- ID pictures: owner or admin/counselor only
- Materials: admin, counselor, class teacher, or enrolled student
- Submissions: admin, counselor, submitting student, or class teacher
- Message attachments: admin or conversation participant

### Rate Limiting
- Per-endpoint rate limits using Django cache with IP + user ID composite keys
- Security spike detection: logs warnings when rate limit thresholds are hit repeatedly
- Notification polling: 120 requests per 60 seconds

### Audit Logging
- All significant actions are logged to `AuditLog` model with: actor, action, target type/ID/label, extra data (JSON), IP address, timestamp
- HMAC-SHA256 hash chain: each entry's hash includes the previous entry's hash for tamper detection
- Integrity verification available on audit log view
- Actions logged: LOGIN, LOGOUT, LOGIN_FAILED, PROFILE_UPDATED, PROFILE_COMPLETED, REGISTRATION_SUBMITTED, PASSWORD_RESET, USER_CREATED, USER_DELETED, USER_UPDATED, CLASS_CREATED, STUDENT_ENROLLED, STUDENT_REMOVED_FROM_CLASS, ASSIGNMENT_CREATED, ASSIGNMENT_DELETED, MATERIAL_UPLOADED, MATERIAL_DELETED, ATTENDANCE_MARKED, SUBMISSION_GRADED, GRADE_CHANGED, MESSAGE_SENT, MESSAGE_REPORTED, MESSAGE_REPORT_RESOLVED, CONCERN_SUBMITTED, INTERVENTION_CREATED, INTERVENTION_UPDATED, ALERT_RESOLVED, REPORT_DOWNLOADED, STUDENT_PROFILE_VIEWED, AUDIT_LOG_EXPORTED, AI_USED, ADMIN_ROLE_CHANGED, MASS_DELETE

---

## Automated System Processes

### Risk Assessment (`calculate_risk` management command)
- Runs automatically on admin dashboard load if last assessment is from a previous day (background thread with cache lock)
- Uses Philippine GPA scale (1.00 = Excellent, 5.00 = Failing)
- Factors: GPA, attendance rate, missing assignments, failing classes, wellness score
- Assigns risk level: Low / Medium / High / Critical

### Alert Generation (Django Signals)
Alerts are auto-created when:
- A student is assessed as **high or critical risk** → `high_risk` alert (severity: critical or high)
- A student has **3+ missing assignments** → `missing_assignments` alert (severity: high if ≥5, else medium)
- Attendance drops **below 75%** → `low_attendance` alert (severity: high if <60%, else medium)
- A teacher submits a concern → `teacher_concern` alert (severity mapped from concern severity: high→critical, medium→high, low→medium)
- Wellness check-in shows distress (stress ≥4, motivation ≤2, or need_help) → `wellness_concern` alert (severity: critical if need_help or stress=5, else high)
- AI sentiment analysis detects high/critical distress in wellness comments → `emotional_distress` alert
- AI creates an intervention → `ai_intervention` alert
- Student is **failing 3+ classes** → `failing_subjects` alert (severity: critical if ≥5, else high)
- Duplicate alerts are prevented (checks for existing unresolved alert of same type for same student)

### Auto-Enrollment (View Logic)
- Student completes profile → enrolled in all classes matching their section AND grade level
- Teacher creates class (via admin) → all students with matching section AND grade level are enrolled

### Student Notifications (Django Signals)
- Intervention scheduled → `Notification` created + email sent to student
- Teacher concern raised → `Notification` created for student

### Real-Time Notifications (5-second polling at `/notifications/poll/`)
- Unread message count (all roles)
- Unread announcement count (students — class + school-wide)
- New grade notifications — submissions graded in last 24 hours (students)
- Unread alert count (counselors and admins)
- Unread student notification count (students — interventions + concerns)
- Total combined count
- Rate limited: 120 requests per 60 seconds

### Content Filtering (Messaging)
- Student messages are filtered for inappropriate language in both Filipino and English before sending
- Matching uses word boundary regex + substring matching on normalized text
- Inappropriate messages are blocked entirely (not filtered/censored)
- `filter_message_content()` utility available for asterisk replacement but blocking is used in practice

### Message Reporting & Consequences
- Any participant can report a message (except own messages; one report per user per message)
- Counselors review reports and apply consequences:
  - **Warning**: email sent to offender
  - **Suspend Messaging**: 1-week suspension + email; user cannot send messages until expiry
  - **Refer to Admin**: email requiring counselor session attendance
  - **No Action**: report closed silently
- Admins can view all message reports (read-only view)
- Admins can lift messaging suspensions manually (sends restoration email)
