# BrightTrack LMS — Role Logic Reference

---

## Student

### Registration & Login
- Students register via **email + student number + password** form at `/register/`
- Student number and email must be pre-approved by admin via CSV upload or manual entry (`ApprovedStudent` table)
- Student number must be exactly **12 digits**
- After submitting the form, an OTP is sent to the email — account is only created after OTP verification
- All roles use the same `/login/` page (email + password), followed by OTP verification
- Forgot password uses OTP flow at `/forgot-password/`
- After registration, redirected to **profile completion** (section, grade level, address, guardian info, profile pic, ID pic)
- Profile completion can be **skipped once** — skip is valid for 7 days, after which the student is forced back to complete it
- After 7-day skip expires, `profile_completed` is reset to False and student is redirected on next dashboard load

### Auto-Enrollment
- When a student completes their profile with a **section + grade level**, they are automatically enrolled in all classes matching **both** values
- Example: Grade 7, Section Apple → enrolled in all "Grade 7 Apple" classes

### Dashboard
- Shows: enrolled classes, upcoming assignments (due soonest), unread announcements, recently graded submissions
- Announcements can be marked read/unread via checkbox (AJAX) — read ones are hidden from dashboard but still visible inside the class
- Live unread announcement count updates in real time

### Classes
- Can view all enrolled classes
- Inside a class: view assignments, announcements, materials, and roster (read-only)

### Assignments
- Three tabs: **Upcoming** (not submitted, not overdue), **Overdue** (not submitted, past due), **Completed** (submitted)
- Submission types depend on what the teacher set: file upload, text entry, or both
- Can re-submit — this clears the previous score and feedback
- Completed tab shows: score (e.g. 8/10), teacher feedback, and teacher comment (even if not yet graded)

### Grades
- Per-class breakdown of all graded assignments
- Shows score, percentage, and feedback/comment per assignment
- Can filter by class

### Attendance
- View overall attendance rate (present/late/absent counts)
- Per-class breakdown with individual records

### Wellness Check-In
- Submit mood check-in: stress level, motivation, workload, sleep quality, need help flag, and optional comments
- If comments contain distress signals (detected by Gemini AI), a high-severity alert is auto-created for counselors
- Can view last 5 check-in history

### Messaging
- Can message teachers, counselors, and other students
- Real-time chat via 3-second polling
- File/image attachments supported
- Content filtering active (Filipino & English profanity)
- Read receipts shown (Messenger-style "Read" under last read sent message)

---

## Teacher

### Login
- Uses **email + password** → OTP verification (same flow as all roles)

### Dashboard
- Shows: classes taught (with student counts), at-risk students (high risk only), recent submissions grouped by class (3 per class), pending grade count
- Section-based breakdowns: students by section, at-risk by section, pending grades by section

### Class Management
- Create class with name, section, grade level, description, schedule, room
- On creation, students with matching section AND grade level are auto-enrolled
- Edit class details (name, description, schedule, room)
- Tabbed class detail: Assignments / Announcements / Materials / Roster
- Quick-action icons in class detail for common tasks

### Student Management
- Add/remove students from a class (only students matching the class section + grade level are shown)
- Bulk add multiple students at once
- Dropping a student removes all their grades, attendance, and submissions for that class

### Assignments
- Create with: title, description, due date, total points, submission type (file / text / both)
- Delete assignment (trash button in class detail)
- View all submissions for an assignment — filter by graded/pending
- Inline preview: expand a submission row to see text content + file before grading
- Leave a comment on a submission via AJAX (no page reload, does not grade)
- Grade submission: enter score + feedback, with optional AI-suggested feedback (Gemini)
- Student is notified when graded

### Attendance
- Mark each student as Present / Absent / Late for today
- Updates existing record if already marked (update_or_create)

### Announcements & Materials
- Post announcements with Normal or Urgent priority
- Upload class materials (files with title and description)
- Delete materials

### Student Monitoring
- View list of all students across teacher's classes — search by name/email, filter by year level or class
- Students sorted by risk level (high first)
- View individual student profile: risk level, GPA, attendance rate, wellness check-ins, concerns, interventions
- Submit a concern about a student: Academic / Behavioral / Emotional / Attendance

### Messaging
- Real-time messaging with students and counselors

---

## Counselor

### Login
- Uses **email + password** → OTP verification (same flow as all roles)

### Dashboard
- Shows: high/medium risk student counts, unread alert badge (updates every 5 seconds), pending interventions, upcoming scheduled interventions
- Section-based breakdown of high and medium risk students
- Quick Actions: Download PDF report, Download DOCX report, BT AI Assistant

### At-Risk Students
- View all students with risk assessments, sorted by risk score
- Filter by risk level (High / Medium / Low), search by name/email, filter by year level
- Click a student to view full profile: risk score, GPA, attendance, wellness history, concerns, interventions
- AI intervention recommendations shown on profile if student is medium/high risk (Gemini)
- Academic pattern analysis also shown (Gemini)

### Interventions
- Create intervention for a student: type, description, scheduled date
- When created, related critical/high alerts for that student are auto-resolved
- Update intervention: change status (Scheduled → Completed / Cancelled), add notes
- Filter by status (Scheduled / Completed / Cancelled / History) and year level
- Bulk auto-create: creates interventions for all students with unresolved critical/high alerts who don't already have a scheduled one

### Alerts
- View all unresolved alerts, color-coded by severity
- Filter by type, severity, show resolved toggle
- Mark individual alert as read
- Resolve individual alert
- Alerts are auto-generated by Django signals (see Automated Processes below)

### Reports
- Risk level distribution (High / Medium / Low counts)
- Intervention statistics (scheduled, completed, cancelled, completion rate)
- Alert statistics (unresolved, resolved, resolution rate, by type)
- Academic overview (average attendance rate, total concerns, total check-ins)
- Age range analysis of high-risk students
- Download as PDF or DOCX

### BT AI Assistant
- Create Intervention, Auto-Create All Interventions, Generate Report, Analyze Behavior, Weekly Summary, Draft Parent Email, Search Student, Ask AI

### Messaging
- Real-time messaging with teachers and students

---

## Admin

### Login
- Uses **email + password** → OTP verification (same flow as all roles)

### Admin Roles (tier-gated sidebar)
- `superadmin` — full access: Create Superuser, System Logs, all lower tiers
- `admin` — Create Class, Create User, Enroll Students, Upload Students
- `registrar` — Enroll Students, Upload Students only

### Dashboard
- System stats: total users, students, teachers, counselors, admins, classes, assignments
- Risk distribution: high/medium/low risk counts
- Top 5 classes by enrollment
- Recent alerts (last 5)
- Unresolved alerts count, pending interventions count
- User activity chart (last 30 days, 5-day intervals)
- Auto-runs risk calculation (`calculate_risk`) on load if assessments are stale (older than today)
- Download PDF / DOCX system report
- BT AI Assistant button

### User Management
- Create teacher or counselor accounts (students self-register via approved list)
- When creating a teacher with subjects + sections + grade level, classes are auto-created for each subject-section combination
- View/search/filter all users by role, name, year level, section
- Delete users (cannot delete admin accounts)
- Cleanup tool: deletes all non-admin users at once (requires typing "DELETE ALL USERS")

### Student Pre-Approval
- Upload CSV to pre-approve students for registration (`ApprovedStudent` table)
- CSV columns: `student_number` (12 digits), `email`, `first_name`, `last_name`, `year_level` (7–10), `section` (optional)
- Or add students manually one at a time via the "Add Manually" tab
- `update_or_create` logic — re-uploading updates existing records
- Registered students are marked `is_registered=True` and cannot re-register

### Class Management
- Create classes and assign to any teacher
- Enroll students into classes manually — multi-select with section/grade/search filters

### System Logs (`/manage/audit-log/`) — superadmin only
- View LOGIN, LOGOUT, LOGIN_FAILED, ADMIN_ROLE_CHANGED events
- Filter by action, actor name, date range
- Paginated (50 per page)

### Django Admin
- Full model-level access at `/admin/`

---

## Authentication & Security

### OTP Flow (all roles)
- Login: credentials verified → OTP sent to email → verify at `/verify-otp/` → logged in
- Register (students): form submitted → OTP sent → verify → account created atomically
- Forgot password: email entered → OTP sent → verify → reset password at `/reset-password/`
- OTP rate limits: 5 verify attempts per email per 30 minutes
- Registration rate limit: 5 attempts per IP per 10 minutes
- `transaction.atomic()` + `select_for_update()` prevents race conditions on registration

### Password Requirements (`StrongPasswordValidator`)
- Minimum 8 characters (Django default)
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character
- Not too common (Django CommonPasswordValidator)

### Session Security
- Registration password stored server-side in Django session between form and OTP step
- Cleared immediately after account creation

---

## Automated System Processes

### Risk Assessment (`calculate_risk` management command)
- Runs automatically on admin dashboard load if last assessment is from a previous day
- Uses Philippine GPA scale (1.00 = Excellent, 5.00 = Failing)
- Factors: GPA, attendance rate, missing assignments, wellness score
- Assigns risk level: Low / Medium / High

### Alert Generation (Django Signals)
Alerts are auto-created when:
- A student is assessed as high risk
- A student has 3+ missing assignments
- Attendance drops below 75%
- A teacher submits a concern
- Wellness check-in detects emotional distress (via Gemini sentiment analysis)

### Auto-Enrollment (Django Signals / View Logic)
- Student completes profile → enrolled in all classes matching their section AND grade level
- Teacher creates class → all students with matching section AND grade level are enrolled

### Real-Time Notifications (5-second polling)
- Unread message count (all roles)
- Unread announcement count (students)
- New grade notifications — submissions graded in last 24 hours (students)
- Unread alert count (counselors and admins)
- Bell icon dropdown with recent notification history (persisted in localStorage per user)

### Content Filtering (Messaging)
- All messages are filtered for inappropriate language in both Filipino and English before sending
