# BrightTrack LMS — Academic Presentation Guide

**System Name:** BrightTrack Learning Management System
**Formerly Known As:** Campus Care
**Live URL:** https://bright-track-project.onrender.com
**Last Updated:** June 2026
**Status:** Fully Deployed and Operational

---

## I. Project Overview

### Background

BrightTrack is a web-based Learning Management System (LMS) developed for junior high school students in Grades 7 through 10. The system was designed to address a gap in existing LMS platforms: the absence of integrated student wellness monitoring and early intervention support.

Traditional LMS platforms focus solely on academic delivery — assignments, grades, and attendance. BrightTrack extends this by incorporating a wellness tracking layer that continuously evaluates each student's academic performance, attendance record, and emotional well-being to produce a composite risk score. When a student's risk level reaches a critical threshold, the system automatically generates alerts and notifies the school counselor, enabling early intervention before academic failure occurs.

### Problem Statement

Junior high school students are vulnerable to academic decline caused by a combination of factors — poor attendance, missed assignments, emotional distress, and lack of timely support. School counselors often lack a centralized, real-time view of student well-being, relying instead on manual reports or teacher referrals that arrive too late.

### Proposed Solution

BrightTrack consolidates academic data, attendance records, wellness check-ins, and teacher concerns into a single platform. An automated risk assessment engine evaluates each student continuously. Counselors receive live alerts, can schedule interventions, and are assisted by an AI assistant (BT AI) powered by Google Gemini for generating recommendations, drafting communications, and producing reports.

---

## II. System Objectives

1. Provide a complete LMS for class management, assignment submission, grading, and attendance tracking.
2. Automate student risk assessment using a multi-factor scoring model (GPA, attendance, missing assignments, wellness).
3. Enable counselors to monitor at-risk students, schedule interventions, and track outcomes.
4. Integrate an AI assistant to support counselors and administrators with data-driven recommendations.
5. Deliver real-time notifications to all user roles through polling-based updates.
6. Provide a secure, role-based access system with OTP authentication for students.
7. Allow users to report inappropriate messages, with counselor review and administrative oversight.

---

## III. Scope and Limitations

### Scope
- Covers four user roles: Student, Teacher, Counselor, and Administrator
- Supports Grades 7 to 10 (Junior High School)
- Deployed on cloud infrastructure (Render) with PostgreSQL database and Cloudinary file storage
- Accessible via web browser on desktop and mobile devices

### Limitations
- Real-time communication uses polling (3–5 second intervals) rather than WebSockets; suitable for the current scale but not optimized for very large concurrent user bases
- AI features depend on the availability of the Google Gemini API
- OTP delivery depends on the Brevo transactional email service
- Audit Log feature is partially implemented (login/logout events only)

---

## IV. Technical Architecture

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Django 5.0 (Python 3.12) |
| Database | PostgreSQL (Render managed, local dev) |
| Authentication | Django Allauth (Google OAuth), custom OTP flow |
| File Storage | Cloudinary (production), local filesystem (development) |
| Frontend | Django Templates, Tailwind CSS, Chart.js, Vanilla JavaScript |
| Static Files | WhiteNoise |
| AI Integration | Google Gemini API |
| Email Delivery | Brevo Transactional Email API |
| Automated Logic | Django Signals |
| Deployment | Render.com (web service + PostgreSQL add-on) |

### Application Modules

| URL Prefix | Django App | Responsibility |
|------------|-----------|----------------|
| `/` | `accounts` | Authentication, registration, profiles, dashboard |
| `/class/` | `academics` | Classes, assignments, submissions, grades, attendance |
| `/wellness/` | `wellness` | Check-ins, risk assessment, alerts, interventions, reports |
| `/messages/` | `messaging` | Inbox, conversations, message reporting |
| `/ai/` | `ai_assistant` | AI-powered counselor and admin assistant |
| `/admin/` | Django Admin | Full model-level administrative access |
| `/accounts/` | allauth | Google OAuth callbacks |

### Data Models Summary

**academics**
- `Class` — name, code, section, year_level (7–10), teacher FK, students M2M, semester, schedule, room
- `Assignment` — class FK, title, description, due_date, total_points, submission_type (file_upload / text_entry / both)
- `Submission` — assignment FK, student FK, file, text_content, score, feedback, comment, graded_at
- `Attendance` — class FK, student FK, date, status (present / absent / late)
- `Announcement` — class FK, author FK, title, content, priority (normal / urgent), read_by M2M
- `Material` — class FK, title, file, uploaded_by FK

**accounts**
- `User` — role (student / teacher / counselor / admin), section, year_level, student_number, profile_picture, id_picture, about_me, subject, gender, profile_completed, admin_role, guardian fields
- `OTPCode` — contact_value (email), code, created_at, is_used
- `ApprovedStudent` — pre-approved student registry for OTP registration gating
- `AuditLog` — actor FK, action, target_type, target_id, ip_address, timestamp

**messaging**
- `Conversation` — participants M2M
- `Message` — conversation FK, sender FK, body, attachment, is_read
- `MessageReport` — reporter FK, message FK, reason, details, status, consequence, counselor_notes, resolved_by FK

**wellness**
- `WellnessCheckIn` — student FK, stress_level, motivation_level, workload_level, sleep_quality, need_help, text_response, date
- `RiskAssessment` — student FK, risk_level (low / medium / high), risk_score, gpa, attendance_rate, missing_assignments, date
- `Alert` — student FK, alert_type, severity, is_read, resolved
- `Intervention` — student FK, counselor FK, intervention_type, description, scheduled_date, status, notes, outcome
- `TeacherConcern` — student FK, teacher FK, concern_type, description
- `Notification` — recipient FK, notif_type, message, is_read, created_at

---

## V. System Features by Role

### 5.1 Student

| Feature | Description |
|---------|-------------|
| OTP Login | Email-based one-time password; 6-digit code, 3-minute expiry, rate-limited |
| Profile Completion | Upload profile picture, ID picture, enter student number, grade level, section |
| Auto-Enrollment | Automatically enrolled in all classes matching grade level and section on profile save |
| Dashboard | Stat cards (classes, pending tasks, unread announcements), upcoming assignments, recent announcements with read toggle |
| Assignment Submission | Submit file, text, or both; re-submission clears previous grade |
| Grades | Per-class breakdown with score, percentage, teacher feedback, and teacher comment |
| Attendance | Overall attendance rate and per-class breakdown |
| Wellness Check-In | Log mood, stress, sleep quality using emoji-based interface |
| Messaging | Real-time chat (3s polling), file attachments, read receipts, content filtering, student-to-student enabled |
| Message Reporting | Report inappropriate messages received from any user; submitted to counselor for review |
| Notifications | Bell dropdown and toast popups for interventions scheduled and teacher concerns raised |

### 5.2 Teacher

| Feature | Description |
|---------|-------------|
| Class Management | Create and edit classes with section and grade level; matching students auto-enrolled |
| Student Management | Manually add or remove students from a class |
| Tabbed Class Detail | Assignments, Announcements, Materials, and Roster tabs |
| Assignment Creation | Set submission type (File / Text / Both), due date, total points |
| Submission Review | Inline preview of student text and file submissions before grading |
| AJAX Commenting | Leave comments on submissions without page reload |
| AI-Assisted Grading | AI Suggest button generates feedback using Google Gemini based on submission content |
| Attendance Marking | Mark each student Present, Absent, or Late per class per day |
| Announcements | Post normal or urgent announcements to a class |
| Materials | Upload and delete class materials (PDF, DOCX, etc.) |
| Concern Submission | Submit academic, behavioral, emotional, or attendance concerns for a student |
| Student Profile View | View a student's risk level, GPA, attendance rate, and wellness history |

### 5.3 Counselor

| Feature | Description |
|---------|-------------|
| Dashboard | At-risk student overview, live alert badge (5s polling), pending interventions, PDF/DOCX download |
| At-Risk Students | Filter by risk level, search by name, sort by risk score; view full student profile |
| Intervention Management | Create, update, and track interventions; add notes and outcomes |
| One Intervention Rule | System enforces one active scheduled intervention per student |
| Bulk Intervention | Auto-create interventions for all high-risk students without a scheduled intervention |
| Alerts | Filter by type and severity; mark read or resolved; view expandable teacher concern details |
| Reports | Risk distribution, intervention statistics, alert statistics, academic overview with Chart.js charts |
| PDF / DOCX Download | Downloadable reports from the dashboard |
| Message Reports | Review reported messages from users; take action (warning, suspend messaging, refer to admin, no action) |
| BT AI Assistant | Eight AI-powered actions: Create Intervention, Auto-Create All, Generate Report, Analyze Behavior, Weekly Summary, Draft Parent Email, Search Student, Ask AI |

### 5.4 Administrator

| Feature | Description |
|---------|-------------|
| Dashboard | System stat cards, risk distribution charts (pie and bar), quick action buttons |
| User Management | Add, edit, and delete users; assign teacher and counselor roles; cleanup inactive users with typed confirmation |
| Class Management | Create classes for teachers; bulk enroll students with section and grade filter |
| Enrollment | Multi-select student enrollment with section and grade level filtering |
| PDF / DOCX Download | Downloadable system reports |
| Message Reports | View all reported messages and counselor actions; monitor whether reports are pending, reviewed, resolved, or dismissed |
| BT AI Assistant | Generate system report and free-form AI queries |
| Django Admin | Full model-level access at `/admin/` |

---

## VI. Key System Workflows

### 6.1 Student Registration and Onboarding

```
Student visits /otp/
    → Enters school email → OTP sent via Brevo
    → Enters 6-digit code (expires in 3 minutes)
    → If new: sets name and password
    → Completes profile (picture, student number, grade level, section, ID picture)
    → System auto-enrolls student in all matching classes
    → Redirected to student dashboard
```

### 6.2 Risk Assessment Pipeline

```
Teacher marks attendance (absent/late)
    → Django Signal fires → Alert created if attendance < 75%

Student misses 3 or more assignments
    → Django Signal fires → Alert created (missing assignments)

Student logs low wellness score
    → WellnessCheckIn saved → Signal evaluates distress threshold

calculate_risk runs (triggered on dashboard load)
    → Combines: GPA + attendance rate + missing assignments + wellness score
    → Produces composite risk_score and risk_level (low / medium / high)
    → RiskAssessment record saved

Risk level = HIGH
    → Alert created → Counselor sees live badge update (5s polling)
    → Counselor opens BT AI → selects student → AI recommends intervention type
    → Intervention created → Student notified (bell + teal toast + Brevo email)
```

### 6.3 Message Reporting Workflow

```
User receives a message they find inappropriate or harmful
    → Clicks the flag icon (🚩) below the message bubble
    → Selects a reason (Harassment, Inappropriate Content, Threat, Hate Speech, Other)
    → Optionally adds details → Submits report

Counselor sees report in sidebar: Messages → Message Reports
    → Reviews reported message content, reporter, and reported user
    → Takes action: Issue Warning / Suspend Messaging / Refer to Admin / No Action
    → Adds counselor notes → Updates status (Reviewed / Resolved / Dismissed)

Admin sees the same reports in their sidebar: Message Reports
    → Views all reports including counselor's action, consequence, and notes
    → Monitors whether reports are pending or have been handled
```

### 6.4 Teacher Grading Workflow

```
Teacher opens Class → Assignments → View Submissions
    → Clicks Preview → expandable row shows student text and file
    → Leaves AJAX comment (no page reload; student sees it immediately)
    → Clicks Grade → enters score and written feedback
    → Optionally clicks AI Suggest → Gemini generates feedback based on submission
    → Student receives graded notification (bell + toast)
```

---

## VII. Authentication and Security

| Mechanism | Implementation |
|-----------|---------------|
| Student Login | OTP email flow — 6-digit code, 3-minute expiry, single-use, rate-limited (3 sends/15 min, 5 attempts/30 min) |
| Staff Login | Username/email and password via `/login/` |
| Google OAuth | Django Allauth integration |
| Forgot Password | OTP-based reset flow |
| Role-Based Access | `@login_required` + `@role_required` decorators on all views |
| CSRF Protection | CSRF tokens on all forms and AJAX requests |
| Content Filtering | Inappropriate word list (Filipino and English) blocks student messages at send time |
| File Validation | `validate_document_upload()` enforces allowed file types on all uploads |
| Secret Management | All credentials stored in environment variables; never committed to source code |
| Production Mode | `DEBUG=False`; WhiteNoise serves static files; Cloudinary serves media |

---

## VIII. Automated Processes

| Process | Trigger | Outcome |
|---------|---------|---------|
| Auto-Enrollment | Student completes profile or teacher creates class | Student added to all matching classes |
| Attendance Alert | Attendance rate drops below 75% | Alert record created; counselor notified |
| Missing Assignment Alert | Student has 3 or more unsubmitted assignments | Alert record created |
| Wellness Distress Alert | Low wellness check-in score | Alert record created |
| Teacher Concern Alert | Teacher submits a concern | Alert created; student notified via bell and toast |
| Intervention Notification | Counselor schedules an intervention | Student receives bell notification, toast popup, and Brevo email |
| Risk Recalculation | Admin or counselor dashboard load | RiskAssessment updated for all students |
| Notification Polling | Every 5 seconds (all authenticated users) | Unread counts and toast popups updated live |
| Message Polling | Every 3 seconds (active conversation) | New messages appended without page reload |

---

## IX. Deployment

### Infrastructure

| Component | Service |
|-----------|---------|
| Web Server | Render.com Web Service |
| Database | Render Managed PostgreSQL |
| File Storage | Cloudinary |
| Email Delivery | Brevo Transactional API |
| Static Files | WhiteNoise (served from Django) |
| Python Version | 3.12.0 |

### Build Process (`build.sh`)

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
```

### Required Environment Variables

```
SECRET_KEY, DEBUG, DATABASE_URL, RENDER_EXTERNAL_HOSTNAME,
ALLOWED_HOSTS, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY,
CLOUDINARY_API_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
GEMINI_API_KEY, BREVO_API_KEY
```

---

## X. Demo Walkthrough

> Live URL: https://bright-track-project.onrender.com

### Step 1 — Student OTP Login
Navigate to `/otp/`. Enter a student email, receive a 6-digit code, enter the code, and proceed to the dashboard. New students are prompted to complete their profile before being auto-enrolled.

### Step 2 — Student Dashboard
Show the stat cards (classes, pending tasks, unread announcements), upcoming assignments with direct submit buttons, and the announcement read toggle that hides items from the dashboard without removing them from the class.

### Step 3 — Assignment Submission
Open a class, go to the Assignments tab, and submit an assignment. Demonstrate all three submission types: file upload, text entry, and both. Show the graded view with score, feedback, and teacher comment.

### Step 4 — Teacher Class Management
Log in as a teacher. Create a class with a section and grade level — show that matching students are auto-enrolled immediately. Open the class and walk through the four tabs: Assignments, Announcements, Materials, Roster.

### Step 5 — Grading with AI Assist
Open a student submission. Show the inline preview, leave an AJAX comment, then grade the submission. Click AI Suggest to demonstrate Gemini generating feedback based on the student's work.

### Step 6 — Attendance Marking
Navigate to Mark Attendance. Mark students as Present, Absent, or Late. Explain that attendance rate feeds directly into the risk score calculation.

### Step 7 — Counselor Dashboard and At-Risk Students
Log in as a counselor. Show the dashboard alert badge updating live. Navigate to At-Risk Students, filter by High risk, and open a student profile showing GPA, attendance rate, wellness history, and existing concerns.

### Step 8 — Intervention and BT AI Assistant
Navigate to `/ai/counselor/`. Demonstrate: Generate Report, Analyze Behavior for a specific student, Draft Parent Email, and Auto-Create All Interventions. Show the collapsible intervention card with AI recommendations (type, success rate, reasoning).

### Step 9 — Message Reporting
Open a conversation. Show the flag icon (🚩) below a received message. Submit a report with a reason and details. Log in as a counselor, navigate to Message Reports in the sidebar, and take action on the report. Log in as admin and show the same report with the counselor's action visible.

### Step 10 — Admin Dashboard
Log in as admin. Show the five stat cards, risk distribution charts, and the PDF/DOCX download buttons. Navigate to Manage Users and demonstrate user creation and role assignment.

### Step 11 — Notifications
Remain on any page and show the bell dropdown updating with new notifications. Trigger a toast popup by sending a message from another account. Explain that notifications persist across page refreshes using browser localStorage.

---

## XI. Known Issues and Pending Items

| Item | Status | Notes |
|------|--------|-------|
| Audit Log | Partial | `log_action()` helper exists; LOGIN/LOGOUT/LOGIN_FAILED are logged. Full AuditLog view and URL are implemented but sidebar link requires `admin_role = superadmin` |
| `admin_role` Tier Gating | Partial | Field exists on User model; sidebar links for Enroll Students, Upload Students, Create Class, Create User, Create Superuser, and System Logs are gated by `admin_role` value |

---

## XII. How the AI Works — No Dataset, No Training Required

### 12.1 The Core Concept

BrightTrack does not use a custom-trained machine learning model. There is no dataset of student records that was used to train the AI, and the system was never taught what a "good" or "bad" student looks like through examples. Instead, BrightTrack uses **Google Gemini**, a large language model (LLM) developed by Google, through its public API.

Gemini is a general-purpose AI that was trained by Google on a massive amount of text from the internet, books, academic papers, and other sources — including educational psychology, counseling literature, and academic intervention research. This means Gemini already understands concepts like academic risk, student stress, attendance patterns, and counseling strategies from its pre-existing training. BrightTrack does not need to teach it any of this.

What BrightTrack does instead is **collect real student data from the database, format it into a structured text prompt, and send that prompt to Gemini**. Gemini reads the data, applies its general knowledge, and returns a recommendation or analysis. This approach is called **prompt engineering** — the skill is in how the question is asked, not in training a model.

---

### 12.2 How Intervention Recommendations Work

When a counselor clicks "Create Intervention" for a student in the BT AI Assistant, the following process occurs:

**Step 1 — Collect student data from the database**

The function `get_student_profile_for_intervention()` in `ml_models/utils.py` queries the database for the student's current situation:

- The student's latest `RiskAssessment` record is retrieved to get their GPA and current risk level
- Attendance records from the last 30 days are counted to calculate the attendance rate
- All assignments in the student's enrolled classes are compared against submitted work to count missing assignments
- The three most recent `WellnessCheckIn` records are averaged to get stress and motivation levels
- Based on these values, a list of specific issues is assembled (e.g., `"low attendance, missing assignments, high stress"`)

The result is a small, structured dictionary:

```
{
  "risk_level": "high",
  "issues": "low attendance, missing assignments, high stress",
  "year_level": 9
}
```

**Step 2 — Build a prompt and send it to Gemini**

The `recommend_intervention()` method in `ml_models/gemini_client.py` takes that profile and inserts it into a text prompt:

```
Recommend top 2 interventions for this at-risk student.

Student Profile:
{
  "risk_level": "high",
  "issues": "low attendance, missing assignments, high stress",
  "year_level": 9
}

Available interventions: One-on-One Counseling, Group Counseling,
Academic Tutoring, Peer Mentoring, Parent Meeting, Study Skills Workshop

Return JSON only:
{
  "recommendations": [
    {
      "type": "intervention name",
      "success_probability": 0.0-1.0,
      "reasoning": "why this will work"
    }
  ]
}
```

This prompt is sent to the Gemini API. Gemini reads the student's issues, draws on its general knowledge of educational interventions, and returns a structured JSON response with two recommended intervention types, an estimated success probability for each, and a plain-language explanation of why each intervention fits the student's situation.

**Step 3 — Create the intervention record**

The system takes Gemini's response and automatically creates an `Intervention` record in the database, scheduled three days from the current date, with the AI-generated summary stored in the description field. The counselor can then review, edit, or update the intervention at any time.

---

### 12.3 How Auto-Create All Interventions Works

The "Auto-Create All Interventions" action in the BT AI Assistant performs the same process described above, but in a loop across every high-risk student who does not already have a scheduled intervention.

The system queries for all `RiskAssessment` records with `risk_level = 'high'`, then filters out any students who already have an intervention with `status = 'scheduled'` (enforcing the one-intervention-per-student rule). For each remaining student, it calls `get_student_profile_for_intervention()`, sends the profile to Gemini, and creates an `Intervention` record. An `Alert` is also created for each student so the counselor can see the activity in the Alerts panel.

The result is that a counselor can process every high-risk student in the school in a single click, with each intervention individually tailored to that student's specific issues — without the counselor having to open each profile manually.

---

### 12.4 How the Risk Score Is Calculated (Without AI)

It is important to clarify that the **risk score itself is not calculated by AI**. The risk assessment is a deterministic formula implemented in Django, not a machine learning prediction. The formula combines four measurable factors:

| Factor | Threshold | Weight in Score |
|--------|-----------|----------------|
| GPA (Philippine scale: 1.00 = Excellent, 5.00 = Failing) | GPA above 3.00 is flagged | High |
| Attendance Rate | Below 75% triggers a flag | High |
| Missing Assignments | 3 or more unsubmitted assignments | Medium |
| Wellness Score | Average of stress, motivation, workload, sleep ratings | Medium |

The system adds weighted penalty points for each failing threshold and produces a numeric `risk_score`. If the score exceeds the high threshold, `risk_level` is set to `'high'`; if it exceeds the medium threshold, it is set to `'medium'`; otherwise it is `'low'`. This calculation runs every time the counselor or admin dashboard is loaded.

The AI is only involved **after** the risk level has already been determined by this formula. Gemini receives the already-computed risk level and issue list, and uses that as context to recommend what type of support would be most appropriate.

---

### 12.5 Why This Approach Is Valid Without a Dataset

A common question is: how can the AI give accurate recommendations if it was never trained on this school's student data?

The answer is that Gemini does not need school-specific training data to understand what interventions work for students with high stress and low attendance. That knowledge already exists in the educational and counseling literature that Gemini was trained on by Google. The system is essentially asking a knowledgeable general AI a specific, data-backed question about a real student.

This is the same principle behind using AI to draft a professional email or summarize a document — the AI does not need to be trained on your specific emails to write one. It applies general language and domain knowledge to the specific context you provide.

The key safeguards in BrightTrack that make this reliable are:

- The AI is never given free-form student text directly; it receives structured, sanitized data fields only (the `_sanitize_for_prompt()` function in `gemini_client.py` strips unsafe characters before any data is sent)
- The AI does not make the final decision — it recommends, and the counselor reviews and acts
- The intervention type is constrained to a fixed list of six options defined in the prompt, so Gemini cannot suggest something outside the school's capabilities
- Responses are cached for 24 hours using Django's cache framework, so repeated requests for the same student profile do not generate inconsistent results
- The risk level and all underlying data are calculated by the system's own deterministic logic before the AI is ever consulted

---

### 12.6 Summary of All AI Actions

| Action | Data Sent to Gemini | What Gemini Returns |
|--------|--------------------|-----------------------|
| Create Intervention | Student risk level, identified issues, year level | Top 2 intervention types with success probability and reasoning |
| Auto-Create All Interventions | Same profile per student, looped | Same recommendation per student |
| Analyze Behavior | Last 30 attendance records, last 20 submission scores, last 10 wellness check-ins | Pattern type, key observations, concerning trends, recommendations |
| Generate Report (Counselor) | Counts of high-risk, medium-risk, unresolved alerts, pending interventions | Formatted narrative report with four sections |
| Generate Report (Admin) | Counts of students, teachers, counselors, high-risk students | Executive summary with four sections |
| Weekly Summary | New alerts, interventions, concerns, high-risk count for the past 7 days | Narrative weekly summary with four sections |
| Draft Parent Email | Student name, risk level, recent teacher concern descriptions | Professional email with subject line and body |
| AI Suggest (Grading) | Assignment description and student submission content | Suggested written feedback for the teacher to use or edit |
| Ask AI | Free-form text question from counselor or admin | Free-form text response |

---

## XIII. Summary

BrightTrack addresses a real gap in school support systems by combining academic management with proactive wellness monitoring. The system is fully deployed, operationally complete, and built on a modern, maintainable stack. Its key differentiators are the automated risk assessment pipeline, the AI-assisted counselor workflow, the message reporting and moderation system, and the real-time notification infrastructure — all working together to support student well-being at the institutional level.
