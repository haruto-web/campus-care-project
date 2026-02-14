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
- ✅ Create new class (name, code, schedule, semester) - *via admin panel*
- ✅ Add/remove students to class - *via admin panel*
- ✅ View class roster - *in dashboard*
- ⏳ Post announcements

**Student Actions:**
- ✅ View enrolled classes - *in dashboard*
- ⏳ See class schedule
- ⏳ Access class materials

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
- ⏳ Post class/school-wide announcements
- ⏳ Set priority (normal/urgent)

**Student Actions:**
- ⏳ View announcements
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
- ⏳ My Classes (detail page)
- ⏳ Class Detail (assignments, grades, announcements)
- ⏳ Assignments (all assignments across classes)
- ⏳ My Grades (detailed view)
- ⏳ Wellness Check-in Form
- ⏳ My Attendance (detailed view)
- ⏳ Profile

### Teacher Pages
- ✅ Login
- ✅ Register
- ✅ Dashboard (classes, students needing attention)
- ⏳ My Classes (detail page)
- ⏳ Class Detail (roster, assignments, attendance)
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
5. ⏳ Class management (CRUD) - *partially done via admin*
6. ⏳ Assignment management (CRUD) - *partially done via admin*
7. ⏳ Grade entry & viewing - *partially done via admin*
8. ⏳ Attendance tracking - *partially done via admin*
9. ✅ Student & Teacher dashboards

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
- ✅ Class enrollment & management - *basic*
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
- ✅ SQLite (development)
- ⏳ PostgreSQL (production)
- ✅ Django ORM

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

### ✅ COMPLETED (40%)
- Database models (all 11 models)
- User authentication (login/register/logout)
- Role-based dashboards (Student, Teacher, Counselor, Admin)
- Admin panel for data management
- Sample data generation
- Basic navigation
- Responsive UI with Bootstrap

### 🔄 IN PROGRESS (30%)
- Class management pages
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
- Reports & analytics
- Charts & visualizations

---

## Next Recommended Steps

1. **Wellness Check-in Form** - Allow students to submit wellness surveys
2. **Teacher Concern Form** - Allow teachers to report student concerns
3. **Class Detail Pages** - Full CRUD for classes (not just admin)
4. **Assignment Submission** - Allow students to submit assignments
5. **Student Profile Page** - Detailed view for counselors/teachers

---

**Last Updated:** February 13, 2026
**Overall Progress:** ~40% Complete
**Status:** Foundation complete, building core features
