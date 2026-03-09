# BrightTrack LMS — Presentation Guide

**Live URL:** https://bright-track-project.onrender.com
**Demo Admin:** `admin@campuscare.com` / `admin123`
**Demo Students:** password `demo1234`

---

## 🎯 What is BrightTrack?

BrightTrack is a **Learning Management System (LMS)** built for junior high school (Grades 7–10) that goes beyond grades and attendance — it actively monitors student wellness and flags at-risk students **before they fall behind**.

> "It's not just an LMS. It's an early warning system for student support."

---

## 👥 Who Uses It?

| Role | What They Do |
|------|-------------|
| **Student** | Submit work, check grades, attend classes, log wellness |
| **Teacher** | Manage classes, grade submissions, track attendance, flag concerns |
| **Counselor** | Monitor at-risk students, create interventions, manage alerts |
| **Admin** | Manage users, classes, enrollment, view system reports |

---

## 🔄 System Flow Overview

```
Student logs in (OTP)
    ↓
Completes profile → Auto-enrolled in matching classes
    ↓
Attends class → Submits assignments → Logs wellness check-ins
    ↓
System calculates risk score (GPA + attendance + wellness + missing work)
    ↓
High risk? → Alert generated → Counselor notified
    ↓
Counselor creates intervention → Tracks outcome
    ↓
Teacher submits concern → Feeds into risk score
    ↓
Admin monitors everything via dashboard + AI reports
```

---

## 🚀 Demo Walkthrough

### Step 1 — Student Login (OTP Flow)
> Go to: https://bright-track-project.onrender.com/otp/

1. Enter a student email → click **Continue**
2. Receive a 6-digit code via email
3. Enter the code → system checks if account exists:
   - **Existing student** → enter password → dashboard
   - **New student** → fill in name + password → profile completion

**Why OTP?** No dummy accounts. Students verify their real email to register. No username/password to forget.

---

### Step 2 — Student Profile Completion
> Happens once after first login

- Upload profile picture
- Enter student number, grade level (7–10), section
- System **auto-enrolls** student into all classes matching their grade + section

---

### Step 3 — Student Dashboard
> `/dashboard/`

Show:
- **Stat cards** — My Classes, Pending Tasks, Unread Announcements (live count)
- **Today's Tasks** — upcoming assignments with Submit button
- **Recent Announcements** — checkbox to mark read (hides from dashboard, stays in class)
- **My Classes sidebar** — quick links

---

### Step 4 — Submitting an Assignment
> Class Detail → Assignments tab → Submit

Three submission types (set by teacher):
- 📎 **File Upload** — attach a document/image
- ✏️ **Text Entry** — type directly in the browser
- 🔀 **File or Text** — student chooses

After grading, student sees:
- Score (e.g., 8/10) with color coding
- Teacher feedback
- Teacher comment (even if not yet graded)

---

### Step 5 — Teacher Dashboard
> Login as teacher

Show:
- Classes taught with student counts
- At-risk students panel
- Recent submissions grouped by class

**Create a class** → enter section + grade level → matching students **auto-enrolled instantly**

---

### Step 6 — Grading a Submission
> Class → Assignments → View Submissions

1. Click **Preview** → expandable row shows student's text + file
2. Leave a **comment** (AJAX — no page reload, student sees it immediately)
3. Click **Grade** → enter score + feedback
4. Click **AI Suggest** → Gemini generates feedback based on submission

---

### Step 7 — Attendance
> Class → Mark Attendance

- Mark each student: Present / Absent / Late
- Attendance rate feeds into the **risk score calculation**

---

### Step 8 — Counselor Dashboard
> Login as counselor

Show:
- High-risk / medium-risk student counts
- Live alert badge (updates every 5 seconds)
- Pending interventions

---

### Step 9 — At-Risk Students
> `/wellness/at-risk/`

- Filter by risk level (High / Medium / Low)
- Search by name
- Click student → full profile: GPA, attendance rate, wellness history, concerns, interventions

**Risk Score is calculated from:**
- GPA (Philippine system: 1.00 = Excellent, 5.00 = Failing)
- Attendance rate (< 75% = flag)
- Missing assignments (3+ = flag)
- Wellness check-in scores

---

### Step 10 — BT AI Assistant (Counselor)
> `/ai/counselor/`

Demonstrate:
1. **Generate Report** → AI summarizes current risk data
2. **Weekly Summary** → what happened this week
3. **Analyze Behavior** → pick a student → AI analyzes attendance + submissions + wellness
4. **Draft Parent Email** → AI writes a professional email for a student's parent
5. **Auto-Create All Interventions** → creates scheduled interventions for all high-risk students in one click

---

### Step 11 — Admin Dashboard
> Login as admin

Show:
- 5 stat cards: Students / Teachers / Counselors / Classes / Students Need Help
- Risk distribution charts (pie + bar)
- Quick Actions: Add Staff, Create Class, Enroll Student, **Download PDF**, **Download DOCX**, **BT AI Assistant**

---

### Step 12 — BT AI Assistant (Admin)
> `/ai/admin/`

- **Generate System Report** → executive summary with student/teacher/counselor/risk counts
- **Ask AI** → free-form questions about the school system

---

### Step 13 — Messaging
> `/messages/`

- Real-time chat (updates every 3 seconds)
- File/image attachments
- Messenger-style **"Read"** receipts
- Content filtering — inappropriate words (Filipino + English) are blocked for students

---

### Step 14 — Notifications (Live Demo)
> Any page — look at the top navbar

- 💬 Chat badge updates live
- 🔔 Bell icon → dropdown with recent notifications
- Toast popups appear for: new messages, new announcements, graded assignments, new alerts
- Notifications **persist across page refreshes** (stored in browser localStorage)

---

## 🧠 Key Technical Highlights

| Feature | How It Works |
|---------|-------------|
| OTP Login | Brevo HTTP API sends 6-digit code; expires in 10 min |
| Auto-Enrollment | Student section + grade level matched to class on profile save |
| Risk Assessment | Django management command `calculate_risk` — runs on admin dashboard load |
| Real-Time | Polling every 3s (chat) and 5s (notifications) — no WebSockets needed |
| AI Feedback | Google Gemini API — grade suggestions + intervention recommendations |
| PDF/DOCX Reports | reportlab + python-docx — downloadable from dashboard |
| File Storage | Cloudinary in production, local in dev |
| Deployment | Render.com — free tier web service + managed PostgreSQL |

---

## 📊 Data Flow: How a Student Becomes "At-Risk"

```
1. Teacher marks student Absent repeatedly
        ↓
2. Django Signal fires → Alert created ("Low attendance")
        ↓
3. Student misses 3+ assignments
        ↓
4. Django Signal fires → Alert created ("Missing assignments")
        ↓
5. Student logs low wellness score
        ↓
6. calculate_risk command runs → combines GPA + attendance + missing work + wellness
        ↓
7. Risk level = HIGH → Alert created → Counselor sees badge update
        ↓
8. Teacher submits concern → feeds into risk profile
        ↓
9. Counselor opens BT AI → clicks "Create Intervention" → picks student
        ↓
10. AI recommends intervention → auto-created → scheduled for 3 days out
```

---

## 🔐 Security Notes (for technical audience)

- All views protected with `@login_required` + role checks
- CSRF tokens on every AJAX call
- OTP codes: single-use, 10-minute expiry
- Secrets in environment variables (never in code)
- Content filtering prevents inappropriate student messages
- `DEBUG=False` in production

---

## 💡 Talking Points

**"Why not just use Google Classroom?"**
> BrightTrack adds the wellness monitoring layer that Google Classroom doesn't have. It connects academic performance, attendance, and emotional health into one risk score — and alerts counselors automatically.

**"How does the OTP login help?"**
> Students don't need to remember a username. They just use their school email. No account creation friction, no forgotten passwords for basic login.

**"What makes the AI useful here?"**
> The AI doesn't replace the counselor — it saves them time. Instead of manually reviewing 50 student profiles, the counselor clicks "Auto-Create All Interventions" and BT handles the scheduling. The counselor reviews and approves.

**"Is it production-ready?"**
> Yes. It's live on Render with a real PostgreSQL database, Cloudinary file storage, and Brevo email delivery. The URL is https://bright-track-project.onrender.com
