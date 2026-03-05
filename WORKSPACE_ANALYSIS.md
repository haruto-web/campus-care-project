# BrightTrack LMS - Complete Analysis

**Last Updated:** March 6, 2026
**Live URL:** https://bright-track-project.onrender.com

---

## 🛠️ **Technology Stack**

### **Backend**
- **Django 5.0** + **Python 3.12** (pinned via `.python-version`)
- **PostgreSQL** — production database (Render)
- **gunicorn** — production WSGI server
- **dj-database-url** — DATABASE_URL parsing
- **psycopg[binary]** — PostgreSQL adapter
- **python-decouple** — environment variable management
- **Pillow** — image processing
- **google-genai** — Gemini AI (feedback suggestions + AI assistant)
- **Django Allauth** — Google OAuth
- **reportlab** — PDF report generation
- **python-docx** — DOCX report generation

### **Frontend**
- **Django Templates** — server-side rendering
- **Tailwind CSS** — utility-first CSS
- **Chart.js** — data visualization
- **Bootstrap Icons** — icon library
- **Vanilla JS** — AJAX, polling, toasts

### **File Storage**
- **Cloudinary** — production media (profiles, submissions, materials, attachments)
- **django-cloudinary-storage** — Cloudinary integration
- **Local FileSystem** — dev media storage
- **WhiteNoise** — static file serving

### **Infrastructure**
- **Render.com** — web service + managed PostgreSQL

### **Email**
- **Brevo HTTP API** — OTP email delivery (`requests.post` to `api.brevo.com/v3/smtp/email`)
- No SMTP — Render free tier blocks all outbound SMTP ports

---

## 📁 **Folder Structure**

```
campus-care-project/
│
├── campus_care/              # Project config
│   ├── settings.py          # DB, apps, middleware, Cloudinary, CSRF, Brevo API key
│   ├── urls.py              # Root URL routing (class/, wellness/, messages/, ai/)
│   └── wsgi.py / asgi.py
│
├── accounts/                 # User management
│   ├── models.py            # Custom User (role, section, year_level, profile_completed)
│   │                        # OTPCode (contact_value, code, is_used, created_at)
│   ├── views.py             # Auth, role dashboards, profile completion, notifications_poll
│   │                        # otp_request_view, otp_verify_view, otp_login_password_view
│   │                        # otp_register_view, otp_forgot_password_view, otp_reset_password_view
│   ├── otp_utils.py         # send_otp_email() via Brevo HTTP API
│   ├── admin_views.py       # Web-based admin tools (manage users, cleanup, enroll)
│   ├── report_views.py      # download_report() → PDF (reportlab) or DOCX (python-docx)
│   ├── urls.py              # Account + admin management + OTP + report routes
│   └── management/commands/ # create_superuser, configure_site, seed_demo
│
├── academics/                # LMS core
│   ├── models.py            # Class, Assignment (submission_type), Submission (text_content),
│   │                        # Attendance, Grade, Announcement (read_by M2M), Material
│   ├── views.py             # Class CRUD, grading, attendance, comment_submission (AJAX),
│   │                        # bulk_add_students
│   ├── announcement_views.py# mark_announcement_read, toggle_announcement_read (AJAX)
│   ├── forms.py             # ClassForm, AssignmentForm, MaterialForm
│   ├── urls.py              # All academic routes under /class/
│   └── templatetags/        # Custom template filters
│
├── wellness/                 # Student support monitoring
│   ├── models.py            # WellnessCheckIn, RiskAssessment, TeacherConcern,
│   │                        # Intervention, Alert
│   ├── views.py             # Risk monitoring, interventions, alerts, reports,
│   │                        # bulk_create_interventions
│   ├── signals.py           # Auto alert generation on risk/attendance/concern events
│   ├── forms.py             # Concern and intervention forms
│   └── urls.py
│
├── messaging/                # Direct messaging
│   ├── models.py            # Conversation (participants M2M), Message (body, attachment, is_read)
│   ├── views.py             # Inbox, conversation thread, poll_messages (returns is_read +
│   │                        # last_read_sent_id for read receipts), AJAX send
│   ├── content_filter.py    # Filipino & English inappropriate word filter (students only)
│   ├── context_processors.py# Unread message count for navbar badge
│   └── urls.py
│
├── ml_models/                # AI/ML
│   ├── gemini_client.py     # Google Gemini API (feedback suggestions, intervention recs)
│   ├── models.py            # PredictionLog, SentimentAnalysis
│   └── utils.py             # Student profile helpers for AI
│
├── ai_assistant/             # BT AI Assistant
│   ├── views.py             # counselor_chat_view, admin_chat_view, counselor_chat, admin_chat
│   └── urls.py              # /ai/counselor/, /ai/admin/, /ai/counselor/chat/, /ai/admin/chat/
│
├── templates/
│   ├── base.html            # Navbar, bell notifications (5s poll), toast popups,
│   │                        # dark mode toggle, hamburger menu, localStorage notif persistence
│   ├── landing.html         # Loading screen + animated progress bar
│   ├── dashboard/
│   │   ├── student_dashboard.html   # Stat cards, tasks, announcements (checkbox toggle)
│   │   ├── teacher_dashboard.html   # Classes, at-risk, recent submissions
│   │   ├── counselor_dashboard.html # At-risk overview, alerts badge, PDF/DOCX buttons
│   │   └── admin_dashboard.html     # 5-col stats, risk charts, PDF/DOCX, BT AI button
│   ├── academics/
│   │   ├── class_detail.html        # Tabbed UI (Assignments/Announcements/Materials/Roster)
│   │   │                            # + icon quick-actions grid
│   │   ├── create_assignment.html   # 3-card radio selector for submission type
│   │   ├── submit_assignment.html   # File/text/both based on submission_type
│   │   ├── view_submissions.html    # Preview toggle + inline comment box (AJAX)
│   │   ├── grade_submission.html    # Two-column grading + AI Suggest button
│   │   └── manage_students.html     # Checkboxes + Select All + bulk Add Selected
│   ├── accounts/
│   │   ├── otp_request.html         # Student login: email → Continue
│   │   ├── otp_verify.html          # Enter 6-digit OTP code
│   │   ├── otp_login_password.html  # Existing student: enter password
│   │   ├── otp_register.html        # New student: name + password
│   │   ├── otp_forgot_password.html # Enter email to reset
│   │   ├── otp_reset_password.html  # Set new password after OTP
│   │   └── student_profile.html     # Teacher view (no AI communication buttons)
│   ├── admin/
│   │   └── enroll_student.html      # Checkbox list + section/grade/search filters
│   ├── ai_assistant/
│   │   ├── counselor_chat.html      # BT AI: 8 quick actions, markdown-rendered chat
│   │   └── admin_chat.html          # BT AI: Generate Report + Ask AI, markdown chat
│   ├── messaging/
│   │   └── conversation.html        # Messenger-style read receipts, file attachments
│   └── wellness/
│       └── view_concerns.html       # Tailwind rewrite with expandable rows
│
├── static/css/custom.css
├── media/                    # Dev uploads only
├── .python-version           # 3.12.0
├── build.sh                  # Render build script (includes seed_demo)
├── requirements.txt          # includes reportlab, python-docx
└── manage.py
```

---

## 🔄 **Website Flow**

### **URL Prefixes**
| Prefix | App |
|--------|-----|
| `/` | accounts |
| `/class/` | academics |
| `/wellness/` | wellness |
| `/messages/` | messaging |
| `/ai/` | ai_assistant |
| `/admin/` | Django admin |
| `/accounts/` | allauth (Google OAuth) |

---

### **1. Authentication & Onboarding**

**Students** use OTP email flow:
```
/otp/  → enter email → OTP sent via Brevo API
    ↓
/otp/verify/ → enter 6-digit code
    ↓
Existing student → /otp/password/ → enter password → dashboard
New student     → /otp/register/ → name + password → profile completion → dashboard
Forgot password → /otp/forgot/   → email → OTP → /otp/reset/ → new password
```

**Staff/Teacher/Admin** use password login:
```
/login/ → email + password → dashboard
```

**Google OAuth** (all roles):
```
/accounts/google/login/ → OAuth → dashboard
```

**Profile Completion** (after first login):
```
Student  → profile pic, student number, grade level (7-10), section, phone, DOB, ID pic
Teacher  → profile pic, section, DOB, ID pic, about me  (or SKIP)
Counselor→ profile pic, DOB  (or SKIP)
    ↓
Auto-enrollment: student section + year_level → matched classes enrolled
```

---

### **2. Teacher Workflow**
```
Teacher Dashboard
  ├─ Classes taught (student counts)
  ├─ At-risk students panel
  ├─ Recent submissions (grouped by class, 3 per class)
  └─ Quick Actions dropdown
        ↓
My Classes (/class/my-classes/) → filter by year/section
        ↓
Class Detail (/class/class/<id>/) — Tabbed UI
  ├─ Assignments tab
  │   ├─ Create Assignment → submission type: File Upload | Text Entry | File or Text
  │   ├─ Delete Assignment (trash button)
  │   └─ View Submissions
  │       ├─ Preview button → expandable row (text_content + file + comment box)
  │       ├─ Save Comment (AJAX, no reload) → student sees it immediately
  │       └─ Grade button → /class/submission/<id>/grade/
  │           └─ Score + Feedback + AI Suggest (Gemini)
  ├─ Announcements tab → Post (normal/urgent)
  ├─ Materials tab → Upload / Delete
  └─ Roster tab → Manage Students (checkboxes + bulk add, year level filter)
        ↓
Mark Attendance (/class/class/<id>/attendance/) → Present/Absent/Late
        ↓
Student Monitoring (/students/) → Submit Concern → Academic/Behavioral/Emotional/Attendance
```

---

### **3. Student Workflow**
```
Student Dashboard (/dashboard/)
  ├─ Stat cards: My Classes | Pending Tasks | Announcements (live unread count)
  ├─ Today's Tasks → upcoming assignments (View/Submit)
  ├─ Recent Announcements
  │   ├─ Only unread shown on dashboard
  │   ├─ Checkbox → marks read (hides from dashboard, stays in class)
  │   └─ Uncheck → restores to dashboard
  └─ My Classes sidebar
        ↓
Class Detail (/class/class/<id>/) — read-only tabbed view
  ├─ Assignments tab → Submit / Re-submit
  │   └─ Submit form adapts to submission_type (file / text / both)
  ├─ Announcements tab → all announcements always visible here
  ├─ Materials tab → download files
  └─ Roster tab → classmates
        ↓
My Assignments (/class/student/assignments/)
  ├─ Upcoming | Overdue | Completed tabs
  └─ Completed tab shows:
      ├─ Score + percentage (color coded)
      ├─ Teacher Feedback (if graded)
      └─ Teacher Comment (shown even if not yet graded)
        ↓
My Grades (/class/student/grades/) → per-class breakdown, feedback row
My Attendance (/class/student/attendance/) → overall rate + per-class
Wellness (/wellness/checkin/) → emoji check-in, history
Messages (/messages/) → real-time chat, read receipts, file attachments
```

---

### **4. Counselor Workflow**
```
Counselor Dashboard
  ├─ At-risk counts (high/medium)
  ├─ Alert badge (5s polling)
  ├─ Pending interventions
  └─ Quick Actions: BT AI Assistant | Download PDF | Download DOCX | View Reports
        ↓
At-Risk Students (/wellness/at-risk/) → filter by risk level, search
  └─ Student Profile → full risk assessment, GPA, attendance, wellness
      └─ Create Intervention
        ↓
Interventions (/wellness/interventions/) → filter by status, update, add notes
        ↓
Alerts (/wellness/alerts/) → color-coded severity, mark read/resolved,
                              bulk create interventions for critical/high
        ↓
Reports (/wellness/reports/) → risk distribution, intervention stats, academic overview
        ↓
BT AI Assistant (/ai/counselor/)
  ├─ Create Intervention (student picker with risk badges)
  ├─ Auto-Create All Interventions (high-risk students)
  ├─ Generate Report (stats + AI summary)
  ├─ Analyze Behavior (attendance + submissions + wellness)
  ├─ Weekly Summary
  ├─ Draft Parent Email
  ├─ Search Student (filter by grade/section/risk)
  └─ Ask AI Anything
```

---

### **5. Admin Workflow**
```
Admin Dashboard → 5-column stats (students/teachers/counselors/classes/high-risk)
  ├─ Risk distribution charts
  ├─ Quick Actions: Add Staff | Create Class | Enroll Student | Advanced Settings
  │                 Download PDF | Download DOCX | BT AI Assistant
  ├─ User Management (/manage/users/) → add/edit/delete, assign roles
  ├─ Cleanup Users (/manage/cleanup-users/)
  ├─ Create Class (/manage/create-class/)
  ├─ Enroll Student (/manage/enroll-student/) → checkbox list + section/grade/search filters
  ├─ BT AI Assistant (/ai/admin/) → Generate System Report | Ask AI
  └─ Django Admin (/admin/) → full model access
```

---

### **6. Messaging System**
```
Navbar chat icon (unread badge, 5s poll)
    ↓
Inbox (/messages/) → all conversations
    ↓
Conversation Thread
  ├─ 3s polling for new messages
  ├─ AJAX send (no page reload)
  ├─ File/image attachments (paperclip)
  ├─ Messenger-style read receipts ("Read" under last read sent message)
  └─ Content filtering (students only — Filipino & English)
```

**Messaging Permissions:**
| Role | Can Message |
|------|-------------|
| Admin | Everyone |
| Counselor | Everyone |
| Teacher | Counselor, Admin, Student |
| Student | Counselor, Teacher, Student |

---

### **7. Real-Time & Notifications**
```
base.html polls /notifications/poll/ every 5s → returns:
  ├─ messages      → unread message count (chat badge)
  ├─ announcements → unread announcement count (students)
  ├─ grades        → assignments graded in last 24h (students)
  └─ alerts        → unresolved alerts (counselors/admins)

Toast popups:
  💬 New message (all roles)
  📢 New announcement (students)
  🏆 Assignment graded (students)
  ⚠️  New alert (counselors/admins)

Bell icon dropdown → notification history persisted in localStorage per user
                     key: notifItems_{{ user.id }}
                     cleared on "Clear All"
```

---

## 🧠 **Key Code Concepts**

### **OTP Model** (`accounts/models.py`)
```python
class OTPCode(models.Model):
    contact_value = models.CharField(max_length=255)  # email
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).seconds < 600

    @classmethod
    def generate(cls, contact_value):
        code = str(random.randint(100000, 999999))
        return cls.objects.create(contact_value=contact_value, code=code)
```

### **OTP Email via Brevo** (`accounts/otp_utils.py`)
```python
def send_otp_email(email, code):
    requests.post('https://api.brevo.com/v3/smtp/email',
        headers={'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'},
        json={'sender': {...}, 'to': [{'email': email}],
              'subject': 'Your BrightTrack verification code',
              'htmlContent': f'<p>Your code: <strong>{code}</strong></p>'},
        timeout=10)
```

### **Settings — Email** (`settings.py`)
```python
BREVO_API_KEY = config('BREVO_API_KEY', default='').strip()
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@brighttrack.com')
# No SMTP settings — Render free tier blocks all outbound SMTP
```

### **Assignment Submission Types** (`academics/models.py`)
```python
SUBMISSION_TYPE_CHOICES = [
    ('file_upload', 'File Upload'),
    ('text_entry', 'Text Entry'),
    ('both', 'File or Text'),
]
```

### **Submission with Text Content** (`academics/models.py`)
```python
class Submission(models.Model):
    text_content = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)  # grade feedback AND teacher comments
    graded_at = models.DateTimeField(null=True, blank=True)
```

### **PDF/DOCX Reports** (`accounts/report_views.py`)
```python
def download_report(request):
    # Accessible to admin and counselor roles
    # ?format=pdf  → reportlab PDF with summary + risk tables
    # ?format=docx → python-docx DOCX with same structure
```

### **Notification Persistence** (`base.html`)
```javascript
const NOTIF_KEY = 'notifItems_{{ user.id }}';
let notifItems = JSON.parse(localStorage.getItem(NOTIF_KEY) || '[]');
// Restored on every page load; cleared on "Clear All"
```

### **Bulk Student Enrollment** (`academics/views.py`)
```python
def bulk_add_students(request, class_id):
    # POST with student[] list → adds all selected students to class
```

### **Auto-Enrollment** (`accounts/views.py` + `academics/views.py`)
```python
# On student profile completion:
section_classes = Class.objects.filter(section__iexact=user.section, year_level=user.year_level)
for cls in section_classes:
    cls.students.add(user)

# On teacher creates class:
students = User.objects.filter(role='student', section__iexact=class_obj.section, year_level=class_obj.year_level)
for student in students:
    class_obj.students.add(student)
```

### **AI Chat Markdown Rendering** (`counselor_chat.html`, `admin_chat.html`)
```javascript
function formatAIResponse(text) {
    return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^---+$/gm, '<hr>')
        .replace(/^#{1,3}\s+(.+)$/gm, '<p class="font-semibold">$1</p>')
        .replace(/^[\*\-]\s+(.+)$/gm, '<div>• $1</div>')
        ...
}
```

---

## ✅ **Features Summary**

### **Authentication & Onboarding**
- Students: OTP email flow (login + register + forgot password)
- Staff/Teacher/Admin: email + password login
- Google OAuth (allauth)
- Role-specific profile completion with skip option
- Auto section + grade level class enrollment on profile completion

### **Teacher**
- Class CRUD with tabbed detail UI + icon quick-actions
- Assignment creation with 3 submission types
- Inline submission preview (text + file) before grading
- AJAX teacher comment on submission (no grade required)
- Grade submission with AI feedback suggestion (Gemini)
- Delete assignment
- Daily attendance marking
- Post announcements (normal/urgent)
- Upload/delete class materials
- Manage students: checkboxes + bulk add
- Student monitoring + concern submission

### **Student**
- Dashboard with live unread announcement count
- Announcement read/unread checkbox toggle (AJAX)
- Submit assignments: file, text, or both
- Re-submit (clears previous grade)
- View score + teacher feedback + teacher comment (even ungraded)
- My Grades, My Attendance, Wellness check-in

### **Counselor**
- At-risk student monitoring with risk filters
- Intervention management (create, update, track)
- Bulk intervention creation for critical/high risk
- Alert management (color-coded, mark read/resolved)
- Reports & analytics
- Download PDF / DOCX reports
- BT AI Assistant (8 actions: interventions, reports, behavior, email drafts, search)

### **Admin**
- Web-based user management (no shell needed)
- Class creation + multi-select student enrollment
- Counselor count stat card (5-column dashboard grid)
- Download PDF / DOCX system reports
- BT AI Assistant (Generate System Report, Ask AI)
- Django admin full model access

### **Messaging**
- Real-time chat (3s polling, AJAX send)
- File/image attachments
- Messenger-style read receipts
- Content filtering (Filipino & English, students only)
- Student-to-student messaging

### **Real-Time**
- 5s notification polling (messages, announcements, grades, alerts)
- Bell dropdown + toast popups per role
- Notification history persisted in localStorage per user

---

## 🚀 **Deployment**

### **Render Environment Variables**
```
SECRET_KEY=<key>
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
BREVO_API_KEY=<xkeysib-...>
DEFAULT_FROM_EMAIL=<sender-email>
```

### **build.sh**
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
python manage.py seed_demo || true
```

### **Python Version**
`.python-version` → `3.12.0` (required — Django 5.0 incompatible with Python 3.14)

### **Demo Credentials**
- Admin: `admin@campuscare.com` / `admin123`
- Demo students: password `demo1234`, section `Demo`, Grade 9

---

## 🔐 **Security**

1. Role-based access control on every view (`@login_required` + role checks)
2. CSRF protection on all AJAX endpoints
3. All secrets in environment variables (`.strip()` on BREVO_API_KEY to avoid `\n`)
4. Cloudinary for secure media in production
5. `DEBUG=False` in production
6. Content filtering prevents inappropriate messages from students
7. OTP codes expire after 10 minutes, single-use
