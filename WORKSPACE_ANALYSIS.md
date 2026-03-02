# BrightTrack LMS - Complete Analysis

## 🛠️ **Technology Stack**

### **Backend Framework**
- **Django 5.0** - Python web framework
- **PostgreSQL** - Production database (Render)
- **python-decouple** - Environment variable management
- **Pillow** - Image processing for profile pictures
- **google-genai** - AI-powered sentiment analysis
- **gunicorn** - Production WSGI server
- **dj-database-url** - Database URL parsing
- **psycopg[binary]** - PostgreSQL adapter (Python 3.11+)

### **Frontend**
- **Django Templates** - Server-side rendering
- **Tailwind CSS** - Modern utility-first CSS framework
- **Chart.js** - Data visualization
- **Bootstrap Icons** - Icon library
- **Custom CSS** - Additional styling

### **File Management**
- **Cloudinary** - Persistent media storage (production)
- **django-cloudinary-storage** - Cloudinary integration
- **Local FileSystem** - Media storage (development)
- **WhiteNoise** - Static file serving

### **Infrastructure**
- **Render.com** - Cloud hosting
- **Cloudinary** - Media CDN

---

## 📁 **Folder Structure**

```
campus-care-project/
│
├── campus_care/              # Main project configuration
│   ├── settings.py          # Database, apps, middleware, auth config
│   ├── urls.py              # Root URL routing
│   └── wsgi.py/asgi.py      # Server deployment
│
├── accounts/                 # User management app
│   ├── models.py            # Custom User model (role-based)
│   ├── views.py             # Auth, dashboards, profiles
│   ├── urls.py              # Account routes
│   ├── admin.py             # Admin panel customization
│   └── management/commands/ # create_superuser, create_dummy_students
│
├── academics/                # LMS core features
│   ├── models.py            # Class, Assignment, Submission, Attendance, Grade, Announcement, Material
│   ├── views.py             # Class management, grading, attendance
│   ├── announcement_views.py# Announcement read tracking (AJAX)
│   ├── forms.py             # Django forms for data input
│   ├── urls.py              # Academic routes
│   └── templatetags/        # Custom template filters
│
├── wellness/                 # Campus Care monitoring system
│   ├── models.py            # WellnessCheckIn, RiskAssessment, TeacherConcern, Intervention, Alert
│   ├── views.py             # Risk monitoring, interventions, alerts, bulk interventions
│   ├── forms.py             # Concern and intervention forms
│   ├── signals.py           # Automated alert generation
│   └── urls.py              # Wellness routes
│
├── messaging/                # Direct messaging system
│   ├── models.py            # Conversation, Message (with file attachments)
│   ├── views.py             # Inbox, conversation thread, compose
│   ├── content_filter.py    # Content filtering for inappropriate language
│   ├── urls.py              # Messaging routes
│   ├── context_processors.py# Unread message count for navbar badge
│   └── management/commands/ # User management and testing tools
│
├── ml_models/                # AI/ML features
│   ├── models.py            # SentimentAnalysis model
│   ├── gemini_client.py     # Google Gemini API integration
│   ├── utils.py             # AI utility functions
│   └── views.py             # AI-related views
│
├── ai_assistant/             # AI chatbot feature
│   ├── views.py             # Chatbot endpoints
│   └── urls.py              # Chatbot routes
│
├── templates/                # HTML templates
│   ├── base.html            # Base layout with navbar + message badge
│   ├── accounts/            # Login, register, profile pages
│   ├── dashboard/           # Role-specific dashboards
│   ├── academics/           # Class, assignment, grading pages
│   ├── wellness/            # Concerns, interventions, alerts
│   └── messaging/           # Inbox, conversation, compose pages
│
├── static/css/              # Custom CSS
├── media/                   # User uploads (dev only)
├── build.sh                 # Render build script
├── runtime.txt              # Python version
└── manage.py                # Django CLI
```

---

## 🔄 **Website Flow**

### **1. Authentication Flow**
```
Landing Page → Register (choose role) → Login → Role-Based Dashboard
```

**User Roles:**
- **Student** - View classes, assignments, grades, wellness check-ins
- **Teacher** - Manage classes, grade assignments, report concerns
- **Counselor** - Monitor at-risk students, create interventions
- **Admin** - Full system access

---

### **2. Teacher Workflow**

```
Teacher Dashboard
    ↓
My Classes → Class Detail
    ↓
├── Manage Students (add/drop with year level filter)
├── Post Announcements (urgent/normal)
├── Upload Materials
├── Create Assignments
├── Mark Attendance (Present/Late/Absent)
├── View Submissions (graded/pending filter) → Grade Assignments
├── Report Student Concerns
└── Messages (direct messaging)
```

---

### **3. Student Workflow**

```
Student Dashboard
    ↓
My Classes → Class Detail
    ↓
├── View Announcements (mark as read via AJAX)
├── Download Materials
├── View/Submit Assignments (with re-submit)
├── View Grades & Feedback
├── Wellness Check-in
└── Messages (direct messaging)
```

---

### **4. Counselor Workflow**

```
Counselor Dashboard
    ↓
├── At-Risk Students List (filter by risk level/year)
│   └── Student Profile → Create Intervention
│
├── Interventions List (filter by status/year)
│   └── Update Intervention (modern UI)
│
├── Alerts (color-coded severity, filter preserved on actions)
│   ├── Bulk Create Interventions (auto-creates for all critical/high)
│   └── Mark as Read/Resolved
│
├── Reports & Analytics (charts, age range analysis)
└── Messages (direct messaging)
```

---

### **5. Messaging System**

```
Navbar (chat icon with unread badge)
    ↓
Inbox → Conversation Thread
    ↓
├── Send text messages
├── Attach files/images (paperclip icon)
├── Content filtering (students only)
└── Compose New Message
    ├── Filter by Role (All/Counselor/Teacher/Student)
    └── Student sub-filters (Year Level + Section)
```

**Messaging Permissions:**
| Role | Can Message |
|---|---|
| Admin | Counselor, Teacher, Student |
| Counselor | Admin, Counselor, Teacher, Student |
| Teacher | Counselor, Admin, Student |
| Student | Counselor, Teacher, Student |

---

## 🧠 **Core Code Concepts**

### **1. Custom User Model** (`accounts/models.py`)
```python
class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES)  # student, teacher, counselor, admin
    year_level = models.IntegerField()
    section = models.CharField()
    profile_picture = models.ImageField()
```

### **2. Messaging Models** (`messaging/models.py`)
```python
class Conversation(models.Model):
    participants = models.ManyToManyField(User)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation)
    sender = models.ForeignKey(User)
    body = models.TextField(blank=True)
    attachment = models.FileField(upload_to='message_attachments/', blank=True)
    is_read = models.BooleanField(default=False)
```

### **3. Content Filtering System** (`messaging/content_filter.py`)
```python
def contains_inappropriate_content(text):
    # Filters Filipino and English inappropriate words
    # Returns (is_inappropriate, found_words)
    # Only applies to students, not staff
```
### **4. Bulk Intervention Creation** (`wellness/views.py`)
```python
def bulk_create_interventions(request):
    # Auto-creates interventions for all critical/high risk students
    # without existing scheduled interventions
    # Marks their alerts as read after creation
```
```

### **5. Django Signals** (`wellness/signals.py`)
Triggers alerts automatically when:
- Risk level becomes high/critical
- Missing assignments ≥ 3
- Attendance < 75%
- Teacher submits concern
- Wellness check-in shows distress

### **6. URL Routing** (`campus_care/urls.py`)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('class/', include('academics.urls')),
    path('wellness/', include('wellness.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('messages/', include('messaging.urls')),
]
```

### **7. Storage Configuration** (`settings.py`)
```python
# Cloudinary in production (DEBUG=False), local in dev (DEBUG=True)
if config('CLOUDINARY_CLOUD_NAME', default='') and not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

---

## 🎯 **Features Summary**

### **Completed (100%)**
✅ User authentication with role-based access
✅ Section & grade level based auto-enrollment
✅ Role-specific profile completion
✅ Teacher class management (CRUD)
✅ Student enrollment with drop feature
✅ Assignment creation and grading (two-column UI)
✅ Student assignment submission with re-submit
✅ Attendance tracking
✅ Announcements with AJAX read tracking
✅ Class materials upload/download/delete
✅ Teacher concern reporting
✅ Risk assessment system
✅ Counselor intervention management (modern UI)
✅ Bulk intervention creation for critical/high risk
✅ Automated alert generation (Django signals)
✅ Color-coded alerts with filter persistence
✅ Reports and analytics dashboard with charts
✅ Modern UI with Tailwind CSS throughout
✅ Recent submissions notifications (teacher)
✅ Recently graded notifications (student)
✅ Year level & section filters
✅ AI-powered sentiment analysis (Gemini)
✅ Student-to-student messaging with content filtering
✅ Content filtering for inappropriate language (Filipino & English)
✅ Enhanced user management tools
✅ AI chatbot assistant (Admin & Counselor)
✅ Direct messaging system with file attachments
✅ Unread message badge in navbar
✅ Role-based message recipient filtering
✅ Mobile responsive navbar (hamburger menu)
✅ Deployed on Render with PostgreSQL

---

## 🚀 **Deployment**

### **Render Environment Variables**
```
SECRET_KEY=...
DEBUG=False
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=yourapp.onrender.com
CLOUDINARY_CLOUD_NAME=campus-care
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
GEMINI_API_KEY=...
```

### **Build Script** (`build.sh`)
```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser      # admin/admin123
python manage.py create_dummy_students # 50 test students
```

### **Default Credentials**
- Admin: `admin` / `admin123`
- Teacher: `demo_teacher` / `teacher123`
- Counselor: `demo_counselor` / `counselor123`
- Students: `student123` (all 50 dummy students)

---

## 🔐 **Security**

1. Role-based access control on every view
2. `@login_required` decorator on all protected views
3. CSRF protection (Django middleware + AJAX fix)
4. Environment variables for all secrets
5. Cloudinary for secure media storage in production
6. `DEBUG=False` in production
