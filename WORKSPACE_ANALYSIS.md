# Campus Care LMS - Complete Analysis

## 🛠️ **Technology Stack**

### **Backend Framework**
- **Django 5.0** - Python web framework
- **PostgreSQL** - Production database
- **python-decouple** - Environment variable management
- **Pillow** - Image processing for profile pictures
- **google-generativeai** - AI-powered sentiment analysis

### **Frontend**
- **Django Templates** - Server-side rendering
- **Tailwind CSS** - Modern utility-first CSS framework
- **Bootstrap 5** - Additional responsive components
- **Chart.js** - Data visualization
- **Custom CSS** - Additional styling

### **File Management**
- **Django Media Files** - Handles uploads (profiles, materials, submissions)
- **Django Static Files** - CSS, JS, images

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
│   └── management/commands/ # Custom commands (sample data)
│
├── academics/                # LMS core features
│   ├── models.py            # Class, Assignment, Submission, Attendance, Grade, Announcement, Material
│   ├── views.py             # Class management, grading, attendance
│   ├── forms.py             # Django forms for data input
│   ├── urls.py              # Academic routes
│   └── templatetags/        # Custom template filters
│
├── wellness/                 # Campus Care monitoring system
│   ├── models.py            # WellnessCheckIn, RiskAssessment, TeacherConcern, Intervention, Alert
│   ├── views.py             # Risk monitoring, interventions, alerts
│   ├── forms.py             # Concern and intervention forms
│   ├── signals.py           # Automated alert generation
│   └── urls.py              # Wellness routes
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
│   ├── base.html            # Base layout with navbar
│   ├── accounts/            # Login, register, profile pages
│   ├── dashboard/           # Role-specific dashboards
│   ├── academics/           # Class, assignment, grading pages
│   └── wellness/            # Concerns, interventions, alerts
│
├── static/css/              # Custom CSS
├── media/                   # User uploads (profiles, materials, submissions)
└── manage.py                # Django CLI
```

---

## 🔄 **Website Flow**

### **1. Authentication Flow**
```
Landing Page → Register (choose role) → Login → Role-Based Dashboard
```

**User Roles:**
- **Student** - View classes, assignments, grades
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
├── Manage Students (add/remove)
├── Post Announcements
├── Upload Materials
├── Create Assignments
├── Mark Attendance
├── View Submissions → Grade Assignments
└── Report Student Concerns
```

**Key Features:**
- Create classes with section & grade level (auto-enrollment)
- Edit class details (rename, schedule, room)
- Search and add/drop students with year level filter
- Post urgent/normal announcements
- Upload/delete PDF/documents for students
- Create assignments with due dates
- Mark attendance (Present/Late/Absent)
- View submissions with status filter (graded/pending)
- Grade submissions with modern two-column UI
- Recent submissions dashboard with notifications
- Report concerns (academic, behavioral, emotional, attendance)
- View student profiles with risk indicators

---

### **3. Student Workflow**

```
Student Dashboard
    ↓
My Classes → Class Detail
    ↓
├── View Announcements (mark as read)
├── Download Materials
├── View Assignments
├── Submit Assignments (with re-submit)
├── View Grades
└── Recently Graded Notifications
```

**Dashboard Shows:**
- Enrolled classes (auto-enrolled by section & grade level)
- Upcoming assignments
- Recently graded work with feedback
- Current GPA
- Attendance rate
- Announcements with read tracking

---

### **4. Counselor Workflow**

```
Counselor Dashboard
    ↓
├── At-Risk Students List (filter by risk level)
│   └── Student Profile → Create Intervention
│
├── Interventions List (filter by status)
│   └── Update Intervention (add notes, outcomes)
│
├── Alerts/Notifications (filter by type)
│   └── Mark as Read/Resolved
│
└── Reports & Analytics
    └── System statistics, charts, trends
```

**Key Features:**
- View students by risk level (High/Medium/Low)
- Access comprehensive student profiles
- Create interventions (counseling, tutoring, parent meetings)
- Track intervention outcomes
- Monitor automated alerts
- Generate reports

---

## 🧠 **Core Code Concepts**

### **1. Custom User Model** (`accounts/models.py`)
```python
class User(AbstractUser):
    role = models.CharField(choices=ROLE_CHOICES)  # student, teacher, counselor, admin
    phone = models.CharField()
    profile_picture = models.ImageField()
```
- Extends Django's built-in User
- Adds role-based access control
- Stores profile pictures

---

### **2. Database Models**

**Academics App:**
- **Class** - Course with teacher, students (ManyToMany), schedule
- **Assignment** - Linked to class, has due date and points
- **Submission** - Student's work, score, feedback
- **Attendance** - Daily records (present/absent/late)
- **Grade** - Calculated from submissions
- **Announcement** - Class or school-wide messages
- **Material** - File uploads for classes

**Wellness App:**
- **WellnessCheckIn** - Student self-assessment (stress, motivation, sleep)
- **RiskAssessment** - Calculated risk score and level
- **TeacherConcern** - Reports from teachers
- **Intervention** - Counselor actions (scheduled/completed/cancelled)
- **Alert** - Automated notifications (high risk, low attendance, etc.)

---

### **3. Role-Based Views** (`accounts/views.py`)

```python
@login_required
def dashboard_view(request):
    if user.role == 'student':
        return student_dashboard(request)
    elif user.role == 'teacher':
        return teacher_dashboard(request)
    elif user.role == 'counselor':
        return counselor_dashboard(request)
```

Each role sees different data:
- **Students** - Their classes, assignments, GPA
- **Teachers** - Classes taught, grading queue, at-risk students
- **Counselors** - High-risk students, alerts, interventions

---

### **4. Permission Checks**

```python
if request.user.role != 'teacher':
    messages.error(request, 'Permission denied.')
    return redirect('dashboard')
```

Every view validates user role before allowing access.

---

### **5. Django Signals** (`wellness/signals.py`)

Automated alert generation:
```python
@receiver(post_save, sender=RiskAssessment)
def create_high_risk_alert(sender, instance, created, **kwargs):
    if instance.risk_level == 'high':
        Alert.objects.create(
            student=instance.student,
            alert_type='high_risk',
            message=f'{instance.student.get_full_name()} is at high risk'
        )
```

Triggers alerts when:
- Risk level becomes high
- Missing assignments ≥ 3
- Attendance < 75%
- Teacher submits concern
- Wellness check-in shows distress

---

### **6. Forms** (`academics/forms.py`, `wellness/forms.py`)

Django ModelForms for data validation:
```python
class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'code', 'description', 'semester', 'schedule', 'room']
```

Handles:
- Input validation
- Error messages
- Database saving

---

### **7. URL Routing**

**Main URLs** (`campus_care/urls.py`):
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),        # /, /login, /register, /profile
    path('class/', include('academics.urls')), # /class/*, /class/create
    path('wellness/', include('wellness.urls')), # /wellness/concerns, /wellness/alerts
]
```

**Academics URLs** (`academics/urls.py`):
- `/class/create/` - Create new class
- `/class/<id>/` - Class detail
- `/class/<id>/students/` - Manage students
- `/class/<id>/assignment/create/` - Create assignment
- `/class/<id>/attendance/` - Mark attendance

**Wellness URLs** (`wellness/urls.py`):
- `/wellness/concern/create/` - Report concern
- `/wellness/at-risk-students/` - At-risk list
- `/wellness/intervention/create/` - Create intervention
- `/wellness/alerts/` - View alerts
- `/wellness/reports/` - Analytics dashboard

---

### **8. Templates & Context**

**Base Template** (`templates/base.html`):
- Navbar with role-based links
- Bootstrap styling
- Django messages display

**Context Data** (passed to templates):
```python
context = {
    'classes': classes,
    'assignments': assignments,
    'attendance_rate': attendance_rate,
}
return render(request, 'template.html', context)
```

---

### **9. File Uploads**

**Settings Configuration:**
```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Model Fields:**
```python
profile_picture = models.ImageField(upload_to='profiles/')
file = models.FileField(upload_to='materials/')
```

Files stored in:
- `media/profiles/` - Profile pictures
- `media/materials/` - Class materials
- `media/submissions/` - Student submissions

---

### **10. Database Queries**

**Filtering:**
```python
# Get teacher's classes
classes = Class.objects.filter(teacher=request.user)

# Get high-risk students
high_risk = RiskAssessment.objects.filter(risk_level='high')

# Get unresolved alerts
alerts = Alert.objects.filter(resolved=False)
```

**Relationships:**
```python
# Get students in a class
class_obj.students.all()

# Get assignments for a class
class_obj.assignments.all()

# Get submissions for an assignment
assignment.submissions.all()
```

---

## 🎯 **Key Features Summary**

### **Completed (100%)**
✅ User authentication with role-based access  
✅ Section & grade level based auto-enrollment  
✅ Role-specific profile completion (Student/Teacher/Counselor)  
✅ Teacher class management (CRUD with edit feature)  
✅ Student enrollment system with drop feature  
✅ Assignment creation and grading  
✅ Student assignment submission with re-submit  
✅ Attendance tracking  
✅ Announcements with read tracking (AJAX)  
✅ Class materials upload/download/delete  
✅ Teacher concern reporting  
✅ Risk assessment system  
✅ Counselor intervention management  
✅ Automated alert generation (Django signals)  
✅ Reports and analytics dashboard  
✅ Modern UI with Tailwind CSS  
✅ Recent submissions notifications  
✅ Recently graded notifications for students  
✅ Year level & section filters  
✅ AI-powered sentiment analysis (Gemini)  
✅ AI chatbot assistant (Admin & Counselor)  

### **Optional Enhancements**
⏳ Password reset functionality  
⏳ Email notifications  
⏳ Direct messaging system  

---

## 📊 **Database Relationships**

```
User (Custom)
  ├── role: student/teacher/counselor/admin
  ├── Classes (as teacher) → Class
  ├── Classes (as student) → Class (ManyToMany)
  ├── Submissions → Submission
  ├── Attendance Records → Attendance
  ├── Risk Assessments → RiskAssessment
  ├── Wellness Check-ins → WellnessCheckIn
  ├── Concerns Received → TeacherConcern
  ├── Interventions → Intervention
  └── Alerts → Alert

Class
  ├── teacher → User (ForeignKey)
  ├── students → User (ManyToMany)
  ├── assignments → Assignment
  ├── attendance_records → Attendance
  ├── announcements → Announcement
  └── materials → Material

Assignment
  ├── class_obj → Class (ForeignKey)
  └── submissions → Submission

Submission
  ├── assignment → Assignment (ForeignKey)
  ├── student → User (ForeignKey)
  ├── score (nullable)
  └── feedback

RiskAssessment
  ├── student → User (ForeignKey)
  ├── risk_level: low/medium/high
  ├── risk_score (calculated)
  ├── gpa
  ├── attendance_rate
  └── missing_assignments

Alert (Auto-generated via Signals)
  ├── student → User (ForeignKey)
  ├── alert_type: high_risk/missing_assignments/low_attendance/wellness_concern/teacher_concern
  ├── is_read (boolean)
  └── resolved (boolean)
```

---

## 🔐 **Security Features**

1. **Role-Based Access Control** - Every view checks user.role
2. **Login Required Decorator** - @login_required on all protected views
3. **Permission Validation** - Teachers can only access their classes
4. **CSRF Protection** - Django's built-in CSRF middleware
5. **Password Hashing** - Django's default password validators
6. **Environment Variables** - Sensitive data in .env file

---

## 🚀 **How to Run**

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials and Gemini API key

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Access at: `http://localhost:8000`

---

## 🎨 **Recent Updates**

### **UI Modernization (Feb 2026)**
- Modern gradient designs with Tailwind CSS
- Student avatars with initials
- Color-coded status badges with animations
- Two-column grading interface
- Interactive hover effects
- AJAX-based announcement read tracking
- Responsive design throughout

### **Auto-Enrollment System**
- Section & grade level based grouping
- Students auto-enrolled in matching classes
- Teachers auto-assigned to section classes
- Class codes auto-generated (SEC-{SECTION})

### **AI Features**
- Sentiment analysis on wellness check-ins
- AI chatbot for counselors and admins
- Automated risk detection
- Concerning phrase identification

---

This is a comprehensive Django-based LMS with integrated student support monitoring, AI-powered sentiment analysis, and automated risk assessment to identify and help at-risk students early.
