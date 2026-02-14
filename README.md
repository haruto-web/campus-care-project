# Campus Care LMS - Complete Workflow (Progress Tracker)

## System Overview
Campus Care is an LMS with integrated student support monitoring that tracks academic performance, attendance, and wellness to identify at-risk students early.

---

## User Roles

- ✅ **Student** - Attend classes, submit assignments, take wellness check-ins
- ✅ **Teacher** - Manage classes, grade assignments, report concerns
- ✅ **Counselor** - Monitor at-risk students, create interventions
- ✅ **Admin** - Manage users, classes, system settings

---

## Core Workflows

### 1. AUTHENTICATION & ONBOARDING

#### 1.1 User Registration/Login
- ✅ Login page (email/username + password)
- ✅ Role-based redirect after login
- ✅ Registration page with role selection
- ⏳ Password reset functionality
- ⏳ First-time setup (profile completion)

#### 1.2 Dashboard (Role-Based Landing)
- ✅ **Student Dashboard**: Classes, upcoming assignments, wellness check-in prompt
- ✅ **Teacher Dashboard**: Classes taught, students needing attention, grading queue
- ✅ **Counselor Dashboard**: At-risk students list, pending interventions
- ✅ **Admin Dashboard**: System statistics, user management

---

### 2. ACADEMIC MANAGEMENT (LMS Core)

#### 2.1 Class/Course Management
**Teacher Actions:**
- ✅ Create new class (name, code, schedule, semester) - *teacher can create*
- ✅ Add/remove students to class - *manage students page with search*
- ✅ View class roster - *class detail page*
- ✅ Post announcements - *class detail page*

**Student Actions:**
- ✅ View enrolled classes - *in dashboard*
- ✅ See class schedule - *dashboard & class detail*
- ✅ Access class materials - *class detail page*

#### 2.2 Assignment Management
**Teacher Actions:**
- ✅ Create assignment (title, description, due date, points) - *via admin panel*
- ⏳ View submissions
- ⏳ Grade assignments
- ⏳ Provide feedback

**Student Actions:**
- ✅ View assignments (upcoming, overdue, completed) - *in dashboard*
- ⏳ Submit assignments
- ⏳ View grades and feedback

#### 2.3 Attendance Tracking
**Teacher Actions:**
- ✅ Mark daily attendance (present/absent/late) - *via admin panel*
- ⏳ View attendance reports per student

**Student Actions:**
- ✅ View own attendance record - *stats in dashboard*

#### 2.4 Grade Management
**Teacher Actions:**
- ✅ Enter grades for assignments/exams - *via admin panel*
- ⏳ Calculate final grades

**Student Actions:**
- ✅ View current grades - *GPA in dashboard*
- ⏳ Track GPA over time

---

### 3. WELLNESS & SUPPORT MONITORING (Campus Care Features)

#### 3.1 Student Wellness Check-ins
**Student Actions:**
- ✅ Weekly self-assessment survey structure created
  - ✅ Stress level (1-5)
  - ✅ Motivation level (1-5)
  - ✅ Workload perception (1-5)
  - ✅ Sleep quality (1-5)
  - ✅ Need help? (Yes/No + optional comment)
- ⏳ Submit check-in form (frontend)
- ✅ View check-in history - *via admin panel*

#### 3.2 Risk Assessment System
**Automated Analysis:**
- ✅ Calculate risk score based on:
  - ✅ Grade trends (declining grades = higher risk)
  - ✅ Missing assignments (count)
  - ✅ Attendance rate (absences)
  - ✅ Wellness check-in responses
- ✅ Assign risk level: **Low / Medium / High**
- ✅ Generate alerts for high-risk students
- ⏳ Automated daily risk calculation (needs scheduling)

#### 3.3 Teacher Concern Reports
**Teacher Actions:**
- ✅ Submit concern about student - *model created*
  - ✅ Student name
  - ✅ Concern type (academic, behavioral, emotional, attendance)
  - ✅ Severity (low/medium/high)
  - ✅ Description
  - ✅ Date observed
- ⏳ Submit concern form (frontend)
- ⏳ View submitted concerns

#### 3.4 At-Risk Student Dashboard
**Counselor/Admin View:**
- ✅ List of students by risk level
- ✅ Filter by: risk level, class, grade - *via admin panel*
- ⏳ Sort by: risk score, last check-in date
- ✅ Quick stats: total at-risk, new alerts - *in dashboard*
- ✅ Student cards showing:
  - ✅ Name, photo, grade, risk level
  - ✅ Key indicators (GPA, attendance %, missing assignments)
  - ⏳ Last wellness check-in
  - ⏳ Recent concerns

#### 3.5 Student Detail/Profile Page
**Counselor/Teacher View:**
- ⏳ Student info (name, email, classes, photo)
- ⏳ Risk level indicator (color-coded)
- ⏳ Academic performance:
  - ⏳ Current GPA
  - ⏳ Grade trends (chart)
  - ⏳ Missing assignments list
- ⏳ Attendance:
  - ⏳ Attendance rate
  - ⏳ Recent absences
- ⏳ Wellness data:
  - ⏳ Check-in history (chart)
  - ⏳ Recent responses
- ⏳ Concerns:
  - ⏳ Teacher-submitted concerns
- ⏳ Interventions:
  - ⏳ Past and current interventions
  - ⏳ Notes from counselors

#### 3.6 Intervention Management
**Counselor Actions:**
- ✅ Create intervention - *model created*
  - ✅ Student
  - ✅ Type (counseling session, tutoring, parent meeting, etc.)
  - ✅ Description
  - ✅ Scheduled date
  - ✅ Status (scheduled/completed/cancelled)
- ⏳ Create intervention form (frontend)
- ⏳ Update intervention status
- ⏳ Add notes after intervention
- ⏳ Track outcomes
- ⏳ Schedule follow-ups

#### 3.7 Alert/Notification System
**Automated Alerts:**
- ✅ Alert model created
- ✅ Email/in-app notification structure for:
  - ✅ Student moves to high risk
  - ✅ Multiple assignments missed
  - ✅ Attendance drops below threshold
  - ✅ Wellness check-in shows distress
  - ✅ Teacher submits concern
- ⏳ Automated alert generation (needs signals)

**Notification Center:**
- ⏳ View all alerts
- ⏳ Mark as read/resolved
- ⏳ Filter by type/date

---

### 4. COMMUNICATION

#### 4.1 Announcements
**Teacher/Admin Actions:**
- ✅ Post class/school-wide announcements
- ✅ Set priority (normal/urgent)

**Student Actions:**
- ✅ View announcements
- ⏳ Mark as read

#### 4.2 Messaging (Optional)
- ⏳ Direct messages between users
- ⏳ Student → Teacher questions
- ⏳ Counselor → Student check-ins

---

## Page Structure & Navigation

### Student Pages
- ✅ Login
- ✅ Register
- ✅ Dashboard (classes, assignments, wellness prompt)
- ✅ My Classes (detail page) - *clickable from dashboard*
- ✅ Class Detail (assignments, grades, announcements, materials, schedule)
- ⏳ Assignments (all assignments across classes)
- ⏳ My Grades (detailed view)
- ⏳ Wellness Check-in Form
- ⏳ My Attendance (detailed view)
- ⏳ Profile

### Teacher Pages
- ✅ Login
- ✅ Register
- ✅ Dashboard (classes, students needing attention)
- ✅ My Classes (detail page) - *clickable from dashboard*
- ✅ Class Detail (roster, assignments, announcements)
- ✅ Create New Class - *form with all fields*
- ✅ Manage Students - *add/remove with search*
- ✅ Post Announcement
- ⏳ Create/Edit Assignment
- ⏳ Grade Assignments
- ⏳ Mark Attendance
- ⏳ Submit Concern
- ⏳ Student Profile View
- ⏳ Profile

### Counselor Pages
- ✅ Login
- ✅ Register
- ✅ Dashboard (at-risk students overview)
- ⏳ At-Risk Students List (detailed)
- ⏳ Student Detail/Profile
- ⏳ Create Intervention
- ⏳ Interventions List
- ⏳ Alerts/Notifications
- ⏳ Reports (analytics)
- ⏳ Profile

### Admin Pages
- ✅ Login
- ✅ Dashboard (system overview)
- ✅ User Management (add/edit/delete users) - *admin panel*
- ✅ Class Management - *admin panel*
- ✅ At-Risk Students - *admin panel*
- ⏳ System Settings
- ⏳ Reports

---

## Development Priority (Build Order)

### ✅ Phase 1: Foundation (Week 1-2)
1. ✅ Django setup
2. ✅ Database models (User, Class, Assignment, Grade, Attendance)
3. ✅ User authentication (login/logout/register)
4. ✅ Basic templates & navigation

### 🔄 Phase 2: LMS Core (Week 3-4) - IN PROGRESS
5. ✅ Class management (CRUD) - *teachers can create/manage classes*
6. ✅ Student enrollment - *teachers can add/remove students with search*
7. ⏳ Assignment management (CRUD) - *partially done via admin*
8. ⏳ Grade entry & viewing - *partially done via admin*
9. ⏳ Attendance tracking - *partially done via admin*
10. ✅ Student & Teacher dashboards
11. ✅ Announcements system
12. ✅ Class materials system

### ⏳ Phase 3: Campus Care Features (Week 5-6)
10. ⏳ Wellness check-in form & storage - *model done, form needed*
11. ⏳ Risk assessment algorithm - *model done, automation needed*
12. ✅ At-risk student dashboard - *basic version done*
13. ⏳ Student detail page with indicators
14. ⏳ Teacher concern form - *model done, form needed*

### ⏳ Phase 4: Intervention & Alerts (Week 7)
15. ⏳ Intervention management - *model done, forms needed*
16. ⏳ Alert/notification system - *model done, automation needed*
17. ✅ Counselor dashboard - *basic version done*

### ⏳ Phase 5: Polish & Testing (Week 8)
18. ⏳ UI/UX improvements
19. ⏳ Reports & analytics
20. ⏳ Testing & bug fixes
21. ⏳ Documentation

---

## Key Features Summary

### LMS Features:
- ✅ Class enrollment & management - *teachers create & manage*
- ✅ Student enrollment - *search & add students*
- ✅ Announcements - *post & view*
- ✅ Class materials - *upload & download*
- ✅ Class schedule - *display*
- ⏳ Assignment submission & grading - *partial*
- ✅ Attendance tracking - *basic*
- ✅ Grade viewing - *basic*

### Campus Care Features:
- ✅ Wellness check-ins - *model created*
- ✅ Automated risk assessment - *model created*
- ✅ Early warning alerts - *model created*
- ✅ Teacher concern reporting - *model created*
- ✅ Intervention tracking - *model created*
- ✅ Support staff dashboard - *basic version*

---

## Technical Stack

### Backend:
- ✅ Django 5.0
- ✅ PostgreSQL (production & development)
- ✅ Django ORM
- ✅ File upload handling

### Frontend:
- ✅ Django Templates
- ✅ Bootstrap 5 (responsive UI)
- ⏳ Chart.js (data visualization)
- ⏳ JavaScript (interactivity)

### Additional:
- ✅ Django Messages (notifications)
- ⏳ Django Signals (automated alerts)
- ⏳ Celery (optional - scheduled tasks)

---

## Current Progress Summary

### ✅ COMPLETED (55%)
- Database models (13 models: Announcement, Material)
- User authentication (login/register/logout)
- Role-based dashboards (Student, Teacher, Counselor, Admin)
- Admin panel for data management
- Class detail pages (Student & Teacher views)
- Teacher class creation (full form)
- Student management (add/remove with search)
- Class roster display
- Announcements system (create & view)
- Class materials system (upload & download)
- Class schedule display
- PostgreSQL database migration
- Media file handling
- Basic navigation
- Responsive UI with Bootstrap

### 🔄 IN PROGRESS (15%)
- Assignment submission system
- Grade entry forms
- Attendance marking interface

### ⏳ TODO (30%)
- Wellness check-in form
- Teacher concern form
- Intervention creation form
- Student detail page
- Automated risk calculation
- Alert automation
- Announcement read status
- Reports & analytics
- Charts & visualizations

---

## Next Recommended Steps (Teacher Focus)

1. **Create Assignment Form** - Allow teachers to create assignments from class page
2. **Mark Attendance Interface** - Allow teachers to mark attendance for enrolled students
3. **View Submissions** - Allow teachers to see student submissions
4. **Grading Interface** - Allow teachers to grade submissions
5. **Teacher Concern Form** - Allow teachers to report student concerns

---

**Last Updated:** February 14, 2026
**Overall Progress:** ~55% Complete
**Status:** Teacher class management complete, focusing on teacher features

---

## Recent Updates (Feb 14, 2026)

### ✅ New Features Added:
1. **Class Detail Pages** - Full view for students and teachers
2. **Teacher Class Creation** - Teachers can create their own classes
3. **Student Management System** - Add/remove students with search functionality
4. **Class Roster Display** - View all enrolled students
5. **Announcements System** - Teachers can post, students can view
6. **Class Materials** - Upload and download course materials
7. **Class Schedule** - Display schedule and room information
8. **PostgreSQL Migration** - Moved from SQLite to PostgreSQL
9. **Media File Handling** - Support for file uploads

### 📁 New Models:
- `Announcement` (title, content, priority, class/school-wide)
- `Material` (title, description, file, class)

### 🔗 New URLs:
- `/class/create/` - Create new class
- `/class/<id>/` - Class detail page
- `/class/<id>/students/` - Manage students
- `/class/<id>/students/add/<student_id>/` - Add student
- `/class/<id>/students/remove/<student_id>/` - Remove student
- `/class/<id>/announcement/create/` - Create announcement

### 📄 New Templates:
- `academics/create_class.html` - Class creation form
- `academics/class_detail.html` - Class detail page
- `academics/manage_students.html` - Student management with search
- `academics/create_announcement.html` - Announcement form

### 🎯 Teacher Features Complete:
- ✅ Create classes with full details
- ✅ Search and add students to classes
- ✅ Remove students from classes
- ✅ View class roster
- ✅ Post announcements
- ✅ View class materials
- ✅ See class schedule
