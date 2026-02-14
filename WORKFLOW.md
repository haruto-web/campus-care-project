# Campus Care LMS - Complete Workflow

## System Overview
Campus Care is an LMS with integrated student support monitoring that tracks academic performance, attendance, and wellness to identify at-risk students early.

---

## User Roles

1. **Student** - Attend classes, submit assignments, take wellness check-ins
2. **Teacher** - Manage classes, grade assignments, report concerns
3. **Counselor** - Monitor at-risk students, create interventions
4. **Admin** - Manage users, classes, system settings

---

## Core Workflows

### 1. AUTHENTICATION & ONBOARDING

**1.1 User Registration/Login**
- Login page (email/username + password)
- Role-based redirect after login
- Password reset functionality
- First-time setup (profile completion)

**1.2 Dashboard (Role-Based Landing)**
- **Student Dashboard**: Classes, upcoming assignments, wellness check-in prompt
- **Teacher Dashboard**: Classes taught, students needing attention, grading queue
- **Counselor Dashboard**: At-risk students list, pending interventions
- **Admin Dashboard**: System statistics, user management

---

### 2. ACADEMIC MANAGEMENT (LMS Core)

**2.1 Class/Course Management**
- **Teacher Actions**:
  - Create new class (name, code, schedule, semester)
  - Add/remove students to class
  - View class roster
  - Post announcements
  
- **Student Actions**:
  - View enrolled classes
  - See class schedule
  - Access class materials

**2.2 Assignment Management**
- **Teacher Actions**:
  - Create assignment (title, description, due date, points)
  - View submissions
  - Grade assignments
  - Provide feedback
  
- **Student Actions**:
  - View assignments (upcoming, overdue, completed)
  - Submit assignments
  - View grades and feedback

**2.3 Attendance Tracking**
- **Teacher Actions**:
  - Mark daily attendance (present/absent/late)
  - View attendance reports per student
  
- **Student Actions**:
  - View own attendance record

**2.4 Grade Management**
- **Teacher Actions**:
  - Enter grades for assignments/exams
  - Calculate final grades
  
- **Student Actions**:
  - View current grades
  - Track GPA

---

### 3. WELLNESS & SUPPORT MONITORING (Campus Care Features)

**3.1 Student Wellness Check-ins**
- **Student Actions**:
  - Weekly self-assessment survey:
    - Stress level (1-5)
    - Motivation level (1-5)
    - Workload perception (1-5)
    - Sleep quality (1-5)
    - Need help? (Yes/No + optional comment)
  - Submit check-in
  - View check-in history

**3.2 Risk Assessment System**
- **Automated Analysis** (runs daily):
  - Calculate risk score based on:
    - Grade trends (declining grades = higher risk)
    - Missing assignments (count)
    - Attendance rate (absences)
    - Wellness check-in responses
  - Assign risk level: **Low / Medium / High**
  - Generate alerts for high-risk students

**3.3 Teacher Concern Reports**
- **Teacher Actions**:
  - Submit concern about student:
    - Student name
    - Concern type (academic, behavioral, emotional, attendance)
    - Severity (low/medium/high)
    - Description
    - Date observed
  - View submitted concerns

**3.4 At-Risk Student Dashboard**
- **Counselor/Admin View**:
  - List of students by risk level
  - Filter by: risk level, class, grade
  - Sort by: risk score, last check-in date
  - Quick stats: total at-risk, new alerts
  - Student cards showing:
    - Name, photo, grade, risk level
    - Key indicators (GPA, attendance %, missing assignments)
    - Last wellness check-in
    - Recent concerns

**3.5 Student Detail/Profile Page**
- **Counselor/Teacher View**:
  - Student info (name, email, classes, photo)
  - Risk level indicator (color-coded)
  - Academic performance:
    - Current GPA
    - Grade trends (chart)
    - Missing assignments list
  - Attendance:
    - Attendance rate
    - Recent absences
  - Wellness data:
    - Check-in history (chart)
    - Recent responses
  - Concerns:
    - Teacher-submitted concerns
  - Interventions:
    - Past and current interventions
    - Notes from counselors

**3.6 Intervention Management**
- **Counselor Actions**:
  - Create intervention:
    - Student
    - Type (counseling session, tutoring, parent meeting, etc.)
    - Description
    - Scheduled date
    - Status (scheduled/completed/cancelled)
  - Update intervention status
  - Add notes after intervention
  - Track outcomes
  - Schedule follow-ups

**3.7 Alert/Notification System**
- **Automated Alerts**:
  - Email/in-app notification when:
    - Student moves to high risk
    - Multiple assignments missed
    - Attendance drops below threshold
    - Wellness check-in shows distress
    - Teacher submits concern
  
- **Notification Center**:
  - View all alerts
  - Mark as read/resolved
  - Filter by type/date

---

### 4. COMMUNICATION

**4.1 Announcements**
- **Teacher/Admin Actions**:
  - Post class/school-wide announcements
  - Set priority (normal/urgent)
  
- **Student Actions**:
  - View announcements
  - Mark as read

**4.2 Messaging (Optional)**
- Direct messages between users
- Student → Teacher questions
- Counselor → Student check-ins

---

## Page Structure & Navigation

### Student Pages
1. Login
2. Dashboard (classes, assignments, wellness prompt)
3. My Classes
4. Class Detail (assignments, grades, announcements)
5. Assignments (all assignments across classes)
6. My Grades
7. Wellness Check-in Form
8. My Attendance
9. Profile

### Teacher Pages
1. Login
2. Dashboard (classes, students needing attention)
3. My Classes
4. Class Detail (roster, assignments, attendance)
5. Create/Edit Assignment
6. Grade Assignments
7. Mark Attendance
8. Submit Concern
9. Student Profile View
10. Profile

### Counselor Pages
1. Login
2. Dashboard (at-risk students overview)
3. At-Risk Students List
4. Student Detail/Profile
5. Create Intervention
6. Interventions List
7. Alerts/Notifications
8. Reports (analytics)
9. Profile

### Admin Pages
1. Login
2. Dashboard (system overview)
3. User Management (add/edit/delete users)
4. Class Management
5. At-Risk Students
6. System Settings
7. Reports

---

## Development Priority (Build Order)

### Phase 1: Foundation (Week 1-2)
1. ✅ Django setup
2. Database models (User, Class, Assignment, Grade, Attendance)
3. User authentication (login/logout)
4. Basic templates & navigation

### Phase 2: LMS Core (Week 3-4)
5. Class management (CRUD)
6. Assignment management (CRUD)
7. Grade entry & viewing
8. Attendance tracking
9. Student & Teacher dashboards

### Phase 3: Campus Care Features (Week 5-6)
10. Wellness check-in form & storage
11. Risk assessment algorithm
12. At-risk student dashboard
13. Student detail page with indicators
14. Teacher concern form

### Phase 4: Intervention & Alerts (Week 7)
15. Intervention management
16. Alert/notification system
17. Counselor dashboard

### Phase 5: Polish & Testing (Week 8)
18. UI/UX improvements
19. Reports & analytics
20. Testing & bug fixes
21. Documentation

---

## Key Features Summary

**LMS Features:**
- Class enrollment & management
- Assignment submission & grading
- Attendance tracking
- Grade viewing

**Campus Care Features:**
- Wellness check-ins
- Automated risk assessment
- Early warning alerts
- Teacher concern reporting
- Intervention tracking
- Support staff dashboard

---

## Technical Stack

**Backend:**
- Django 5.0
- SQLite (development) / PostgreSQL (production)
- Django ORM

**Frontend:**
- Django Templates
- Bootstrap 5 (responsive UI)
- Chart.js (data visualization)
- JavaScript (interactivity)

**Additional:**
- Django Messages (notifications)
- Django Signals (automated alerts)
- Celery (optional - scheduled tasks)

---

## Next Steps

1. Create database models
2. Set up URL routing
3. Build authentication system
4. Create base templates
5. Start with Student & Teacher dashboards
