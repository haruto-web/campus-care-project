# BrightTrack LMS - Complete Workflow (Progress Tracker)

## System Overview
BrightTrack (formerly Campus Care) is an LMS with integrated student support monitoring that tracks academic performance, attendance, and wellness to identify at-risk students early.

**Last Updated:** March 2, 2026
**Overall Progress:** 100% Complete
**Status:** All features complete! Real-time chat, global notifications, responsive design, content filtering, and user management added!

---

## 🎯 SYSTEM WORKFLOW

### Registration & Onboarding Flow
```
1. User visits landing page (with loading screen) → Clicks "Register"
2. Selects role (Student/Teacher/Counselor/Admin)
3. Role-specific fields appear:
   - Student: Year Level (7-10) + Section
   - Teacher: Section (class they teach)
   - Counselor: Basic info only
4. Completes registration → Auto-login
5. Redirected to role-specific profile completion:
   - Student: Profile pic, student number, grade level, section, phone, DOB, ID pic
   - Teacher: SKIP (goes directly to dashboard)
   - Counselor: SKIP (goes directly to dashboard)
6. Section & Grade Level based auto-assignment:
   - Students: Auto-enrolled in classes matching BOTH section AND year level
   - Example: Grade 7 Section Apple → Only enrolled in Grade 7 Apple classes
   - Teacher: Auto-assigned to section class during registration
7. Redirected to role-based dashboard
```

### Teacher Workflow
```
1. Login → Dashboard
   ├─ View classes taught
   ├─ See students needing attention (at-risk)
   └─ Check recent submissions (with notifications)

2. Create New Class
   ├─ Enter Class Name (e.g., "Math")
   ├─ Enter Section (e.g., "Apple")
   ├─ Select Grade Level (7, 8, 9, or 10)
   ├─ Add Description, Semester, Room, Schedule
   └─ Students with matching section AND grade level auto-enrolled

3. My Classes
   ├─ Filter by year level/section
   ├─ Click class → Class Detail Page
   └─ Edit class name/details

4. Class Management
   ├─ Edit Class → Rename, update details
   ├─ Manage Students → Add/drop students with search and year level filter
   ├─ Create Assignment → Title, description, due date, points
   ├─ Mark Attendance → Present/Late/Absent
   ├─ Post Announcement → Normal/Urgent priority
   └─ Upload Materials → Files for students

5. Grading
   ├─ View Submissions → Filter graded/pending
   ├─ Grade Assignment → Two-column UI with feedback
   └─ Student notified automatically

6. Student Monitoring
   ├─ Students List → Search, filter by year level
   ├─ View Student Profile → Risk level, GPA, attendance
   └─ Submit Concern → Academic/behavioral/emotional
```

### Student Workflow
```
1. Login → Dashboard
   ├─ View enrolled classes (auto-enrolled by section + grade level)
   ├─ See upcoming assignments
   ├─ Check recently graded work
   ├─ Read announcements (mark as read)
   └─ Click stat cards → expand classes list or missing assignments by subject

2. My Classes
   ├─ Click class → Class Detail
   ├─ View assignments, grades, materials
   └─ See class schedule and teacher info

3. Assignments
   ├─ View all assignments (upcoming/overdue/completed)
   ├─ Submit assignment → Upload file
   └─ Re-submit if needed

4. Academic Tracking
   ├─ My Grades → View scores and feedback
   ├─ My Attendance → Track attendance rate
   └─ GPA displayed on dashboard

5. Wellness
   ├─ Submit wellness check-in
   └─ View check-in history

6. Communication
   ├─ View announcements
   ├─ Download class materials
   ├─ Mark announcements as read
   └─ Real-time messaging with teachers/counselors/students (content filtered)
```

### Counselor Workflow
```
1. Login → Dashboard
   ├─ View at-risk students overview
   ├─ See new alerts count (real-time badge)
   └─ Check pending interventions

2. At-Risk Students
   ├─ Filter by risk level (High/Medium/Low)
   ├─ Search by name/email
   ├─ View student profile → Full risk assessment
   └─ Create intervention

3. Interventions
   ├─ View all interventions
   ├─ Filter by status (Scheduled/Completed/Cancelled)
   ├─ Update intervention → Add notes, change status
   └─ Track outcomes

4. Alerts
   ├─ View all alerts (color-coded by severity)
   ├─ Filter by type/severity
   ├─ Mark as read
   └─ Resolve alerts

5. Reports
   ├─ Risk level distribution
   ├─ Intervention statistics
   ├─ Alert statistics
   └─ Academic overview
```

### Admin Workflow
```
1. Login → Dashboard
   ├─ System statistics (users, classes, assignments)
   ├─ Risk distribution charts
   └─ Recent alerts

2. User Management (Admin Panel)
   ├─ Add/edit/delete users
   ├─ Assign roles
   └─ View all users

3. Class Management (Admin Panel)
   ├─ View all classes
   ├─ Create classes for teachers
   └─ Enroll students

4. System Monitoring
   ├─ View at-risk students
   ├─ Check wellness history
   └─ Monitor system usage
```

### Automated System Processes
```
1. Section & Grade Level Based Assignment (On Profile Completion)
   ├─ Student enters section + year level → Auto-enrolled in matching classes
   ├─ Example: Grade 7 Section Apple → Only Grade 7 Apple classes
   ├─ Teacher creates class with section + grade level → Auto-enrolls matching students
   └─ Code auto-generated: "SEC-{SECTION}" (e.g., SEC-APPLE)

2. Alert Generation (Django Signals)
   ├─ High risk student detected → Alert created
   ├─ 3+ missing assignments → Alert created
   ├─ Attendance < 75% → Alert created
   ├─ Teacher submits concern → Alert created
   └─ Wellness distress detected → Alert created

3. Real-Time Notifications (Polling)
   ├─ Chat messages → 3s polling, AJAX send (no page reload)
   ├─ Unread message badge → updates every 5s
   ├─ New announcement → toast popup for students
   ├─ Assignment graded → toast popup for students
   ├─ New alert → toast popup for counselors/admins
   └─ Bell icon dropdown shows recent notification history
```

---

## User Roles

- ✅ **Teacher** - Manage classes, grade assignments, report concerns
- ✅ **Counselor** - Monitor at-risk students, create interventions
- ✅ **Admin** - Manage users, classes, system settings
- ✅ **Student** - Attend classes, submit assignments, take wellness check-ins

---

## 1. TEACHER FEATURES (100% Complete)

### ✅ Class Management
- ✅ Create class with section AND grade level
- ✅ Auto-enroll students matching both section and grade level
- ✅ Edit class (rename, description, schedule, room)
- ✅ Add/remove students to class (with search and year level filter)
- ✅ View class roster
- ✅ View class detail page
- ✅ Section & grade level based automatic grouping

### ✅ Assignment Management
- ✅ Create assignment (title, description, due date, points)
- ✅ View submissions (modern UI with student avatars)
- ✅ Grade assignments with feedback (modern two-column layout)
- ✅ View grading queue
- ✅ Recent submissions dashboard widget

### ✅ Attendance Tracking
- ✅ Mark daily attendance (present/absent/late)
- ✅ View attendance interface

### ✅ Communication
- ✅ Post class/school-wide announcements
- ✅ Set priority (normal/urgent)
- ✅ Upload class materials
- ✅ Delete materials
- ✅ Real-time messaging with students/counselors

### ✅ Student Monitoring
- ✅ Submit concern about student (academic, behavioral, emotional, attendance)
- ✅ View submitted concerns
- ✅ View comprehensive student profiles
- ✅ Search and filter students
- ✅ View students needing attention

---

## 2. COUNSELOR FEATURES (100% Complete)

### ✅ Dashboard
- ✅ At-risk students overview
- ✅ Quick stats (total at-risk, new alerts)
- ✅ Pending interventions
- ✅ Real-time alert badge (updates every 5s)

### ✅ Student Monitoring
- ✅ View student profiles with risk indicators
- ✅ Filter by risk level, class, grade
- ✅ Search students by name or email
- ✅ Sort by risk score

### ✅ Intervention Management
- ✅ Intervention model created (type, description, scheduled date, status)
- ✅ Create intervention form
- ✅ Update intervention status (modern Tailwind UI)
- ✅ Add notes after intervention
- ✅ Track outcomes
- ✅ View all interventions with filters

### ✅ Alerts & Notifications
- ✅ Alert model created
- ✅ View all alerts
- ✅ Mark as read/resolved
- ✅ Filter by type/date/severity
- ✅ Automated alert generation (signals)
- ✅ Real-time toast notifications

### ✅ Reports & Analytics
- ✅ System-wide statistics
- ✅ Risk level distribution
- ✅ Intervention statistics
- ✅ Alert statistics
- ✅ Academic overview
- ✅ Recent activity tracking

---

## 3. ADMIN FEATURES (100% Complete)

### ✅ User Management
- ✅ Add/edit/delete users (via admin panel)
- ✅ View all users
- ✅ Role assignment

### ✅ Class Management
- ✅ View all classes (via admin panel)
- ✅ Manage class data
- ✅ Create classes for teachers
- ✅ Enroll students in classes

### ✅ System Monitoring
- ✅ Dashboard with system statistics
- ✅ At-risk students view (via admin panel)
- ✅ View wellness check-in history
- ✅ Data visualization (charts and graphs)

---

## 4. STUDENT FEATURES (100% Complete)

### ✅ Class Access
- ✅ View enrolled classes
- ✅ See class schedule
- ✅ Access class materials (download)
- ✅ View class detail page

### ✅ Assignment Management
- ✅ View assignments (upcoming, overdue, completed)
- ✅ Submit assignments (with file upload)
- ✅ View grades and feedback
- ✅ Re-submit assignments

### ✅ Attendance & Grades
- ✅ View own attendance record (stats in dashboard)
- ✅ View current GPA (in dashboard)
- ✅ My Attendance (detailed view)
- ✅ My Grades (detailed view)

### ✅ Wellness Check-ins
- ✅ Submit check-in form
- ✅ View check-in history

### ✅ Communication
- ✅ View announcements
- ✅ Mark announcements as read (with checkbox)
- ✅ Real-time messaging with teachers/counselors/students
- ✅ Content filtering for inappropriate language (students only)
- ✅ Student-to-student messaging enabled

### ✅ Dashboard Stat Cards (Clickable)
- ✅ Classes card → expands full class list
- ✅ Missing card → expands missing assignments grouped by subject

---

## 5. AUTHENTICATION & ONBOARDING (100% Complete)

### ✅ User Registration/Login
- ✅ Login page (email/username + password)
- ✅ Google OAuth login
- ✅ Role-based redirect after login
- ✅ Registration page with role selection
- ✅ First-time setup (role-based profile completion)
- ✅ Automatic section + grade level based class assignment

### ✅ Profile Completion (Role-Based)
- ✅ **Student Profile**: Profile picture, student number, grade level, section, phone, DOB, ID picture
- ✅ **Teacher Profile**: Profile picture, section, DOB, ID picture, about me
- ✅ **Counselor Profile**: Profile picture, DOB
- ✅ Skip option available

---

## 6. REAL-TIME FEATURES (100% Complete)

### ✅ Chat / Messaging
- ✅ AJAX message send (no page reload)
- ✅ 3-second polling for new messages
- ✅ "Live" green pulse indicator in chat header
- ✅ File/image attachments
- ✅ Role-based messaging permissions
- ✅ Student-to-student messaging enabled
- ✅ Content filtering for inappropriate language (Filipino & English)
- ✅ Real-time error handling for blocked messagesole-based messaging permissions

### ✅ Global Notification Polling (5s)
- ✅ Unread message badge updates live
- ✅ Bell icon with dropdown notification history
- ✅ Toast popups for:
  - 💬 New message (all roles)
  - 📢 New announcement (students)
  - 🏆 Assignment graded (students)
  - ⚠️ New alert (counselors/admins)

---

## 7. UI/UX (100% Complete)

### ✅ Responsive Design
- ✅ Mobile-first layouts across all pages
- ✅ Collapsible hamburger menu
- ✅ 2-column stat grids on mobile
- ✅ Shortened button labels on small screens
- ✅ Hidden table columns on mobile (submissions page)

### ✅ Landing Page
- ✅ Loading screen with animated progress bar
- ✅ Fade-out transition after page load
- ✅ Hero, features, roles, CTA sections
- ✅ Mobile-responsive navigation

### ✅ Dark Mode
- ✅ Toggle in navbar dropdown
- ✅ Persists via localStorage

---

## Technical Stack

### Backend:
- ✅ Django 5.0
- ✅ PostgreSQL (production & development)
- ✅ Django ORM
- ✅ File upload handling (Cloudinary in production)
- ✅ Django Allauth (Google OAuth)
- ✅ Django Signals (automated alerts)

### Frontend:
- ✅ Django Templates
- ✅ Tailwind CSS (responsive UI, dark mode)
- ✅ Chart.js (data visualization)
- ✅ JavaScript (polling, AJAX, toasts)

### Deployment:
- ✅ Render (production)
- ✅ Cloudinary (media storage in production)
- ✅ WhiteNoise (static files)
- ✅ PostgreSQL on Render

---

## Recent Updates (March 2, 2026)

### ✅ New Features Added:
1. **Content Filtering System** - Blocks inappropriate language in student messages (Filipino & English)
2. **Student-to-Student Messaging** - Students can now message other students
3. **Enhanced User Management** - Admin tools for user cleanup and management
4. **Improved Message UI** - Cleaner, simpler new message interface
5. **Role-Based Messaging Permissions** - Refined messaging rules for all user types
6. **Real-Time Error Handling** - Immediate feedback for blocked messages

### 🔗 Updated Features:
- Content filter with 40+ inappropriate words/phrases
- Student messaging permissions expanded
- User data validation and cleanup tools
- Enhanced error messages and user feedback

### 📝 Updated Files:
- `messaging/content_filter.py` - Content filtering system
- `messaging/views.py` - Enhanced message validation
- `templates/messaging/new_message.html` - Simplified UI
- `messaging/management/commands/` - User management tools

---

## 🚀 Deployment Checklist

### Render Environment Variables Required:
```
SECRET_KEY=<your-secret-key>
DEBUG=False
DATABASE_URL=<render-postgres-url>
ALLOWED_HOSTS=<render-hostname>
CLOUDINARY_CLOUD_NAME=campus-care
CLOUDINARY_API_KEY=<key>
CLOUDINARY_API_SECRET=<secret>
GOOGLE_CLIENT_ID=<id>
GOOGLE_CLIENT_SECRET=<secret>
RENDER_EXTERNAL_HOSTNAME=bright-track-project.onrender.com
```

### build.sh runs:
```
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
```

### Google OAuth Setup:
- Authorized JS origin: `https://bright-track-project.onrender.com`
- Redirect URI: `https://bright-track-project.onrender.com/accounts/google/login/callback/`
- Django Site domain: `bright-track-project.onrender.com`

---

## ✅ Project Complete!

**BrightTrack LMS** is fully functional with:
- ✅ Complete LMS features (classes, assignments, grades, attendance)
- ✅ Integrated wellness monitoring & risk assessment
- ✅ Real-time chat and notifications with content filtering
- ✅ Student-to-student messaging with safety controls
- ✅ Automatic section + grade level based enrollment
- ✅ Role-based workflows (Student, Teacher, Counselor, Admin)
- ✅ Modern, responsive UI with dark mode
- ✅ Google OAuth login
- ✅ Content filtering for inappropriate language
- ✅ Comprehensive user management tools
- ✅ Deployed on Render with Cloudinary storage

**Live URL:** https://bright-track-project.onrender.com 🎉
