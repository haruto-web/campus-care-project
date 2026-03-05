# BrightTrack LMS - Complete Analysis

**Last Updated:** March 3, 2026
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
- **google-genai** — Gemini AI (feedback suggestions + sentiment)
- **Django Allauth** — Google OAuth

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

---

## 📁 **Folder Structure**

```
campus-care-project/
│
├── campus_care/              # Project config
│   ├── settings.py          # DB, apps, middleware, Cloudinary, CSRF
│   ├── urls.py              # Root URL routing (class/, wellness/, messages/, ai/)
│   └── wsgi.py / asgi.py
│
├── accounts/                 # User management
│   ├── models.py            # Custom User (role, section, year_level, profile_completed)
│   ├── views.py             # Auth, role dashboards, profile completion, notifications_poll
│   ├── admin_views.py       # Web-based admin tools (manage users, cleanup, enroll)
│   ├── urls.py              # Account + admin management routes
│   └── management/commands/ # create_superuser, configure_site
│
├── academics/                # LMS core
│   ├── models.py            # Class, Assignment (submission_type), Submission (text_content),
│   │                        # Attendance, Grade, Announcement (read_by M2M), Material
│   ├── views.py             # Class CRUD, grading, attendance, comment_submission (AJAX)
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
├── ai_assistant/             # AI feedback endpoint
│   ├── views.py             # /ai/teacher/feedback/<id>/ — AI grade suggestion
│   └── urls.py
│
├── templates/
│   ├── base.html            # Navbar, bell notifications (5s poll), toast popups,
│   │                        # dark mode toggle, hamburger menu
│   ├── landing.html         # Loading screen + animated progress bar
│   ├── dashboard/
│   │   ├── student_dashboard.html   # Stat cards, tasks, announcements (checkbox toggle)
│   │   ├── teacher_dashboard.html   # Classes, at-risk, recent submissions
│   │   ├── counselor_dashboard.html # At-risk overview, alerts badge
│   │   └── admin_dashboard.html     # System stats, risk charts
│   ├── academics/
│   │   ├── class_detail.html        # Tabbed UI (Assignments/Announcements/Materials/Roster)
│   │   │                            # + icon quick-actions grid
│   │   ├── create_assignment.html   # 3-card radio selector for submission type
│   │   ├── submit_assignment.html   # File/text/both based on submission_type
│   │   ├── view_submissions.html    # Preview toggle + inline comment box (AJAX)
│   │   └── grade_submission.html    # Two-column grading + AI Suggest button
│   ├── messaging/
│   │   └── conversation.html        # Messenger-style read receipts, file attachments
│   └── wellness/                    # Check-in, alerts, interventions, reports
│
├── static/css/custom.css
├── media/                    # Dev uploads only
├── .python-version           # 3.12.0
├── build.sh                  # Render build script
├── requirements.txt
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
```
Landing Page (loading screen + progress bar)
    ↓
Register (students only via public form) → Auto-login
    ↓
Profile Completion (role-specific):
  Student  → profile pic, student number, grade level (7-10), section, phone, DOB, ID pic
  Teacher  → profile pic, section, DOB, ID pic, about me  (or SKIP)
  Counselor→ profile pic, DOB  (or SKIP)
    ↓
Auto-enrollment: student section + year_level → matched classes enrolled
    ↓
Role-based Dashboard
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
  └─ Roster tab → Manage Students (add/drop, year level filter)
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
  └─ Pending interventions
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
```

---

### **5. Admin Workflow**
```
Admin Dashboard → system stats, risk charts, recent alerts
  ├─ User Management (/manage/users/) → add/edit/delete, assign roles
  ├─ Cleanup Users (/manage/cleanup-users/)
  ├─ Create Class (/manage/create-class/)
  ├─ Enroll Student (/manage/enroll-student/)
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
  ├─ messages  → unread message count (chat badge)
  ├─ announcements → unread announcement count (students)
  ├─ grades    → assignments graded in last 24h (students)
  └─ alerts    → unresolved alerts (counselors/admins)

Toast popups:
  💬 New message (all roles)
  📢 New announcement (students)
  🏆 Assignment graded (students)
  ⚠️  New alert (counselors/admins)

Bell icon dropdown → recent notification history
```

---

## 🧠 **Key Code Concepts**

### **Assignment Submission Types** (`academics/models.py`)
```python
class Assignment(models.Model):
    SUBMISSION_TYPE_CHOICES = [
        ('file_upload', 'File Upload'),
        ('text_entry', 'Text Entry'),
        ('both', 'File or Text'),
    ]
    submission_type = models.CharField(max_length=20, choices=..., default='file_upload')
```

### **Submission with Text Content** (`academics/models.py`)
```python
class Submission(models.Model):
    text_content = models.TextField(blank=True)   # for text_entry / both
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)        # used for both grade feedback AND teacher comments
    graded_at = models.DateTimeField(null=True, blank=True)
```

### **Announcement Read Toggle** (`academics/announcement_views.py`)
```python
def toggle_announcement_read(request, announcement_id):
    # Adds user to read_by if not present, removes if present
    # Returns {'success': True, 'is_read': bool}
    # Dashboard hides read announcements; class detail always shows all
```

### **Teacher Comment (AJAX)** (`academics/views.py`)
```python
def comment_submission(request, submission_id):
    # POST /class/submission/<id>/comment/
    # Saves feedback without touching score or graded_at
    # Student sees comment immediately in assignments/grades pages
```

### **Read Receipts** (`messaging/views.py`)
```python
def poll_messages(request, conversation_id):
    # Returns messages with is_read per message
    # Returns last_read_sent_id (last sent message read by recipient)
    # Frontend shows "Read" only under that message
```

### **Notifications Poll** (`accounts/views.py`)
```python
def notifications_poll(request):
    # Single endpoint polled every 5s
    # Returns: messages, announcements, grades, alerts counts
```

### **Storage Config** (`settings.py`)
```python
# Cloudinary active only in production
if CLOUDINARY_CLOUD_NAME and not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
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

---

## ✅ **Features Summary**

### **Authentication & Onboarding**
- Role-based login (student/teacher/counselor/admin)
- Google OAuth (allauth)
- Student public registration
- Role-specific profile completion with skip option
- Auto section + grade level class enrollment

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

### **Admin**
- Web-based user management (no shell needed)
- Class creation + student enrollment tools
- Django admin full model access
- System stats dashboard

### **Messaging**
- Real-time chat (3s polling, AJAX send)
- File/image attachments
- Messenger-style read receipts
- Content filtering (Filipino & English, students only)
- Student-to-student messaging

### **Real-Time**
- 5s notification polling (messages, announcements, grades, alerts)
- Bell dropdown + toast popups per role
- Chat live indicator

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
```

### **build.sh**
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
```

### **Python Version**
`.python-version` → `3.12.0` (required — Django 5.0 incompatible with Python 3.14)

---

## 🔐 **Security**

1. Role-based access control on every view (`@login_required` + role checks)
2. CSRF protection on all AJAX endpoints
3. All secrets in environment variables
4. Cloudinary for secure media in production
5. `DEBUG=False` in production
6. Content filtering prevents inappropriate messages from students


i want to remove of creating dummy account for student. the student must input email or number to login of register a account. for example student input a email, the student will recieve a OTP/authentication code to put that in register or login. guide me to implement this in my work

create a md file for this implementation