# Campus Care - Student Support Monitoring System

A comprehensive Django-based LMS with integrated student support monitoring that tracks academic performance, attendance, and wellness to identify at-risk students early.

## 🎯 Features

### LMS Core
- ✅ Class enrollment & management
- ✅ Assignment submission & grading
- ✅ Attendance tracking
- ✅ Grade viewing & GPA calculation

### Campus Care (Student Support)
- ✅ Wellness check-ins
- ✅ Automated risk assessment
- ✅ Early warning alerts
- ✅ Teacher concern reporting
- ✅ Intervention tracking
- ✅ Support staff dashboard

### User Roles
- **Student** - View classes, submit assignments, wellness check-ins
- **Teacher** - Manage classes, grade assignments, report concerns
- **Counselor** - Monitor at-risk students, create interventions
- **Admin** - Full system access and management

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/haruto-web/campus-care-project.git
cd campus-care-project
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run migrations
```bash
python manage.py migrate
```

4. Create sample data
```bash
python manage.py create_superuser
python manage.py create_sample_data
python manage.py create_wellness_data
```

5. Run the server
```bash
python manage.py runserver
```

6. Visit http://localhost:8000

## 🎨 Design

**Color Palette: Calm & Trustworthy**
- Primary: #4A90E2 (Soft Blue)
- Success: #50C878 (Emerald Green)
- Danger: #E74C3C (Coral Red)

## 📱 Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Teacher | teacher1 | teacher123 |
| Counselor | counselor1 | counselor123 |
| Student | student1-5 | student123 |

## 🛠️ Tech Stack

- **Backend:** Django 5.0
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Django Templates, Bootstrap 5
- **Icons:** Bootstrap Icons

## 📊 Progress

- ✅ Database models (11 models)
- ✅ Authentication system
- ✅ Role-based dashboards
- ✅ Landing page
- ✅ Admin panel
- 🔄 Wellness forms (in progress)
- 🔄 Class management pages (in progress)

## 📄 License

This project is for educational purposes.

## 👥 Contributors

- Haruto Web

---

**Campus Care** - Empowering educators to support every student's success 💙
