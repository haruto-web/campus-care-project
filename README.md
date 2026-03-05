# BrightTrack LMS - Complete Workflow (Progress Tracker)

## System Overview
BrightTrack (formerly Campus Care) is an LMS with integrated student support monitoring that tracks academic performance, attendance, and wellness to identify at-risk students early.

**Last Updated:** March 3, 2026
**Overall Progress:** 100% Complete
**Live URL:** https://bright-track-project.onrender.com

---

## 🗂️ URL Structure

All academics routes are mounted under `/class/` (not `/academics/`):

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

## 🎯 SYSTEM WORKFLOW

### Registration & Onboarding Flow
```
1. User visits landing page (loading screen + animated progress bar) → Clicks "Register"
2. Fills in name, email, username, password (students only via public registration)
3. Completes registration → Auto-login
4. Redirected to role-specific profile completion:
   - Student: Profile pic, student number, grade level (7-10), section, phone, DOB, ID pic
   - Teacher: Profile pic, section, DOB, ID pic, about me (or SKIP)
   - Counselor: Profile pic, DOB (or SKIP)
5. Section & Grade Level based auto-enrollment:
   - Student enters section + year level → Auto-enrolled in ALL classes matching BOTH
   - Example: Grade 7 Section Apple → Only Grade 7 Apple classes
   - Teacher creates class with section + grade level → Auto-enrolls matching students
6. Redirected to role-based dashboard
```

### Teacher Workflow
```
1. Login → Dashboard
   ├─ View classes taught (with student counts)
   ├─ See at-risk students needing attention
   ├─ Check recent submissions (grouped by class, 3 per class)
   └─ Quick Actions dropdown (create class, mark attendance, etc.)

2. Create New Class (/class/create/)
   ├─ Enter Class Name, Section, Grade Level (7-10)
   ├─ Add Description, Semester, Room, Schedule
   └─ Students with matching section AND grade level auto-enrolled

3. My Classes (/class/my-classes/)
   ├─ Filter by year level / section
   ├─ Click class → Class Detail (tabbed UI)
   └─ Edit class name/details

4. Class Detail (/class/class/<id>/) — Tabbed UI
   ├─ Assignments tab → List with delete button per assignment
   ├─ Announcements tab → List of posted announcements
   ├─ Materials tab → Uploaded files with delete
   ├─ Roster tab → Enrolled students
   └─ Icon quick-actions grid (Create Assignment, Mark Attendance, Post Announcement, Upload Material, Manage Students, Edit Class)

5. Assignment Management
   ├─ Create Assignment → Title, description, due date, points, submission type
   │   └─ Submission types: File Upload | Text Entry | File or Text (radio card selector)
   ├─ View Submissions (/class/class/<id>/assignment/<id>/submissions/)
   │   ├─ Filter by graded/pending
   │   ├─ Preview button → Inline expandable row showing text entry + file
   │   ├─ Comment box in preview row → AJAX save (no page reload)
   │   └─ Grade button → Full grade submission page
   ├─ Grade Submission → Score input, feedback textarea, AI Suggest button
   └─ Delete Assignment → Trash button in class detail

6. Attendance (/class/class/<id>/attendance/)
   └─ Mark Present / Absent / Late per student for today

7. Communication
   ├─ Post Announcement → Title, content, Normal/Urgent priority
   ├─ Upload Material → File with title and description
   └─ Real-time messaging with students/counselors (content filtered)

8. Student Monitoring
   ├─ Students List (/students/) → Search, filter by year level/class
   ├─ View Student Profile → Risk level, GPA, attendance, concerns, interventions
   └─ Submit Concern → Academic / Behavioral / Emotional / Attendance
```

### Student Workflow
```
1. Login → Dashboard (/dashboard/)
   ├─ Stat cards: My Classes | Pending Tasks | Announcements (live unread count)
   ├─ Today's Tasks → Upcoming assignments with View/Submit button
   ├─ Recent Announcements → Unread only shown; checkbox to mark read/unread
   │   └─ Checking = hides from dashboard (stays in class); unchecking = restores
   └─ My Classes sidebar → Quick links to each class

2. My Classes (/class/my-classes/)
   └─ Click class → Class Detail (read-only view)

3. Class Detail (/class/class/<id>/)
   ├─ Assignments tab → Submit / Re-submit button per assignment
   ├─ Announcements tab → All class announcements (always visible here)
   ├─ Materials tab → Download files
   └─ Roster tab → See classmates

4. Assignments (/class/student/assignments/)
   ├─ Tabs: Upcoming | Overdue | Completed
   ├─ Submit → File upload, text entry, or both (based on assignment type)
   ├─ Completed tab shows:
   │   ├─ Score (e.g., 8/10) with color coding
   │   ├─ Teacher Feedback (if graded)
   │   └─ Teacher Comment (if comment-only, shown under "Pending Grade")
   └─ Re-submit clears previous grade/feedback

5. My Grades (/class/student/grades/)
   ├─ Filter by class
   ├─ Score, percentage, status per assignment
   └─ Feedback/comment row shown below each graded assignment

6. My Attendance (/class/student/attendance/)
   ├─ Overall attendance rate
   └─ Per-class breakdown with records

7. Wellness (/wellness/checkin/)
   ├─ Submit mood/wellness check-in (emoji buttons, mobile-friendly)
   └─ View check-in history

8. Messaging (/messages/)
   ├─ Inbox → All conversations
   ├─ Real-time chat (3s polling, AJAX send)
   ├─ File/image attachments
   ├─ Read receipts (Messenger-style "Read" under last read sent message)
   ├─ Content filtering for inappropriate language (Filipino & English)
   └─ Student-to-student messaging enabled
```

### Counselor Workflow
```
1. Login → Dashboard
   ├─ At-risk students overview (high/medium counts)
   ├─ Real-time alert badge (updates every 5s)
   └─ Pending interventions

2. At-Risk Students (/wellness/at-risk/)
   ├─ Filter by risk level (High/Medium/Low)
   ├─ Search by name/email
   ├─ View student profile → Full risk assessment, GPA, attendance, wellness
   └─ Create intervention from profile

3. Interventions (/wellness/interventions/)
   ├─ Filter by status (Scheduled/Completed/Cancelled)
   ├─ Update status, add notes
   └─ Track outcomes

4. Alerts (/wellness/alerts/)
   ├─ Color-coded by severity
   ├─ Filter by type/date/severity
   ├─ Mark as read / Resolve
   └─ Auto-generated by Django signals

5. Reports (/wellness/reports/)
   ├─ Risk level distribution
   ├─ Intervention statistics
   ├─ Alert statistics
   └─ Academic overview
```

### Admin Workflow
```
1. Login → Dashboard
   ├─ System statistics (users, classes, assignments)
   ├─ Risk distribution charts
   └─ Recent alerts

2. User Management (/manage/users/)
   ├─ Add/edit/delete users
   ├─ Assign roles
   └─ Cleanup inactive users (/manage/cleanup-users/)

3. Class Management (/manage/create-class/, /manage/enroll-student/)
   ├─ Create classes for teachers
   └─ Enroll students manually

4. Django Admin (/admin/)
   └─ Full model-level access (users, classes, submissions, etc.)
```

### Automated System Processes
```
1. Section & Grade Level Based Enrollment
   ├─ Student completes profile → Auto-enrolled in matching classes
   └─ Teacher creates class → Auto-enrolls matching students

2. Alert Generation (Django Signals)
   ├─ High risk student detected → Alert created
   ├─ 3+ missing assignments → Alert created
   ├─ Attendance < 75% → Alert created
   ├─ Teacher submits concern → Alert created
   └─ Wellness distress detected → Alert created

3. Real-Time Notifications (Polling every 5s)
   ├─ Unread message badge → live update
   ├─ Bell icon dropdown → recent notification history
   └─ Toast popups:
       ├─ 💬 New message (all roles)
       ├─ 📢 New announcement (students)
       ├─ 🏆 Assignment graded (students)
       └─ ⚠️ New alert (counselors/admins)

4. Risk Assessment (calculate_risk management command)
   ├─ Philippine GPA system (1.00 = Excellent, 5.00 = Failing)
   ├─ Auto-runs on admin dashboard load if stale
   └─ Factors: GPA, attendance rate, missing assignments, wellness score
```

---

## 📦 Data Models

### academics app
- **Class** — name, code, section, year_level (7-10), teacher FK, students M2M, semester, schedule, room
- **Assignment** — class_obj FK, title, description, due_date, total_points, submission_type (file_upload/text_entry/both)
- **Submission** — assignment FK, student FK, file, text_content, score, feedback, graded_at
- **Attendance** — class_obj FK, student FK, date, status (present/absent/late)
- **Announcement** — class_obj FK, author FK, title, content, priority (normal/urgent), read_by M2M
- **Material** — class_obj FK, title, file, uploaded_by FK
- **Grade** — student FK, class_obj FK, assignment FK, score, max_score

### accounts app
- **User** — role (student/teacher/counselor/admin), section, year_level, student_number, profile_picture, id_picture, about_me, profile_completed

### messaging app
- **Conversation** — participants M2M
- **Message** — conversation FK, sender FK, body, attachment, is_read

### wellness app
- **WellnessCheckIn** — student FK, mood score, text_response, date
- **RiskAssessment** — student FK, risk_level (low/medium/high), risk_score, gpa, date
- **Alert** — student FK, alert_type, severity, is_read, resolved
- **Intervention** — student FK, counselor FK, type, description, scheduled_date, status, notes
- **TeacherConcern** — student FK, teacher FK, concern_type, description

---

## 1. TEACHER FEATURES

### ✅ Class Management
- ✅ Create class with section AND grade level
- ✅ Auto-enroll students matching both section and grade level
- ✅ Edit class (rename, description, schedule, room)
- ✅ Add/remove students (with search and year level filter)
- ✅ View class roster
- ✅ Tabbed class detail page (Assignments / Announcements / Materials / Roster)
- ✅ Icon quick-actions grid in class detail

### ✅ Assignment Management
- ✅ Create assignment with submission type (File Upload / Text Entry / File or Text)
- ✅ Delete assignment
- ✅ View submissions with inline preview (text + file) before grading
- ✅ Leave comment on submission (AJAX, no page reload)
- ✅ Grade assignment with score + feedback (two-column layout)
- ✅ AI Suggest feedback button (Gemini)
- ✅ Student notified on grading

### ✅ Attendance
- ✅ Mark daily attendance (present/absent/late)

### ✅ Communication
- ✅ Post announcements (normal/urgent)
- ✅ Upload/delete class materials
- ✅ Real-time messaging with students/counselors

### ✅ Student Monitoring
- ✅ Submit concern (academic/behavioral/emotional/attendance)
- ✅ View student profiles (risk, GPA, attendance, wellness)
- ✅ Search and filter students by year level/class

---

## 2. COUNSELOR FEATURES

### ✅ Dashboard
- ✅ At-risk overview, alert badge (5s polling), pending interventions

### ✅ Student Monitoring
- ✅ Filter by risk level, search by name/email, sort by risk score

### ✅ Intervention Management
- ✅ Create, update, track interventions with notes and outcomes

### ✅ Alerts
- ✅ View, filter, mark read/resolved; auto-generated by signals

### ✅ Reports
- ✅ Risk distribution, intervention stats, alert stats, academic overview

---

## 3. ADMIN FEATURES

### ✅ User Management
- ✅ Add/edit/delete users, assign roles, cleanup tools

### ✅ Class Management
- ✅ Create classes for teachers, enroll students

### ✅ System Monitoring
- ✅ Dashboard stats, risk charts, wellness history

---

## 4. STUDENT FEATURES

### ✅ Dashboard
- ✅ Unread announcements with read/unread checkbox toggle
- ✅ Read announcements hidden from dashboard (still visible in class)
- ✅ Live unread announcement count
- ✅ Upcoming assignments, my classes sidebar

### ✅ Assignments
- ✅ View upcoming/overdue/completed tabs
- ✅ Submit: file upload, text entry, or both
- ✅ Re-submit (clears previous grade)
- ✅ View score, teacher feedback, and teacher comment (even if not yet graded)

### ✅ Grades
- ✅ Per-class grade breakdown with score, percentage, feedback
- ✅ Teacher comments shown even for ungraded submissions

### ✅ Attendance
- ✅ Overall rate + per-class breakdown

### ✅ Wellness
- ✅ Submit check-in (mobile-friendly emoji buttons)
- ✅ View check-in history

### ✅ Messaging
- ✅ Real-time chat (3s polling, AJAX)
- ✅ File/image attachments
- ✅ Messenger-style read receipts
- ✅ Content filtering (Filipino & English)
- ✅ Student-to-student messaging

---

## 5. AUTHENTICATION & ONBOARDING

- ✅ Login (username/email + password)
- ✅ Google OAuth (allauth)
- ✅ Role-based redirect after login
- ✅ Student public registration
- ✅ Role-specific profile completion with skip option
- ✅ Auto section + grade level class enrollment on profile completion

---

## 6. REAL-TIME FEATURES

- ✅ Chat: 3s polling, AJAX send, live indicator, read receipts
- ✅ Notifications: 5s polling, bell dropdown, toast popups
- ✅ Announcement read/unread toggle (AJAX, dashboard only)
- ✅ Teacher comment save (AJAX, no reload)

---

## 7. UI/UX

- ✅ Tailwind CSS, dark mode (localStorage toggle)
- ✅ Mobile-first responsive design, hamburger menu
- ✅ Landing page with loading screen + animated progress bar
- ✅ Tabbed class detail page
- ✅ Inline submission preview with expandable rows

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
| AI | Google Gemini API (feedback suggestions) |
| Signals | Django Signals (automated alerts) |

---

## 🚀 Deployment

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

### Python Version
`.python-version` → `3.12.0` (required for Django 5.0 compatibility)

### Google OAuth
- Authorized JS origin: `https://bright-track-project.onrender.com`
- Redirect URI: `https://bright-track-project.onrender.com/accounts/google/login/callback/`

---

## Recent Changes (March 3, 2026)

1. **Submission Types** — File Upload / Text Entry / File or Text per assignment
2. **Inline Submission Preview** — Teachers can preview text + file before grading
3. **Teacher Comments** — AJAX comment on submission without grading
4. **Student sees comments** — Feedback shown even for ungraded submissions
5. **Announcement Read/Unread Toggle** — Checkbox on dashboard; hides read, stays in class
6. **Read Receipts** — Messenger-style "Read" under last read sent message
7. **Python 3.12 pin** — Fixed Django 5.0 incompatibility with Python 3.14 on Render
8. **URL fixes** — All hardcoded `/academics/` URLs corrected to `/class/`
9. **Delete Assignment** — Trash button in class detail
10. **Tabbed Class Detail** — Assignments / Announcements / Materials / Roster tabs
