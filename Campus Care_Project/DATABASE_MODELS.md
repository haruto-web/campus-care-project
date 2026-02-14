# Campus Care Database Models

## ✅ Models Created Successfully

### 1. ACCOUNTS APP (User Management)

**User Model** (Custom User)
- Extends Django's AbstractUser
- Fields: role (student/teacher/counselor/admin), phone, profile_picture
- Handles authentication for all user types

---

### 2. ACADEMICS APP (LMS Features)

**Class Model**
- Fields: name, code, description, teacher, students (M2M), semester
- Represents courses/classes in the system

**Assignment Model**
- Fields: class_obj, title, description, due_date, total_points
- Assignments created by teachers

**Submission Model**
- Fields: assignment, student, content, file, score, feedback, graded_at
- Student assignment submissions with grading

**Attendance Model**
- Fields: class_obj, student, date, status (present/absent/late), notes
- Daily attendance tracking

**Grade Model**
- Fields: student, class_obj, assignment, score, max_score, date
- Grade records for students

---

### 3. WELLNESS APP (Campus Care Features)

**WellnessCheckIn Model**
- Fields: student, date, stress_level, motivation_level, workload_level, sleep_quality, need_help, comments
- Weekly student self-assessment surveys

**RiskAssessment Model**
- Fields: student, date, risk_level (low/medium/high), risk_score, gpa, attendance_rate, missing_assignments, notes
- Automated risk calculation for students

**TeacherConcern Model**
- Fields: student, teacher, concern_type, severity, description, date_observed, resolved
- Teacher-submitted concerns about students

**Intervention Model**
- Fields: student, counselor, intervention_type, description, scheduled_date, status, notes, outcome
- Counselor interventions and tracking

**Alert Model**
- Fields: student, alert_type, message, is_read, resolved
- System-generated alerts for at-risk students

---

## Database Relationships

```
User (1) ----< (M) Class [as teacher]
User (M) ----< (M) Class [as students]
User (1) ----< (M) WellnessCheckIn
User (1) ----< (M) RiskAssessment
User (1) ----< (M) TeacherConcern [as student]
User (1) ----< (M) TeacherConcern [as teacher]
User (1) ----< (M) Intervention [as student]
User (1) ----< (M) Intervention [as counselor]
User (1) ----< (M) Alert

Class (1) ----< (M) Assignment
Class (1) ----< (M) Attendance
Class (1) ----< (M) Grade

Assignment (1) ----< (M) Submission
Assignment (1) ----< (M) Grade
```

---

## Next Steps

1. ✅ Models created
2. ✅ Migrations applied
3. ✅ Admin registered
4. ⏳ Create superuser
5. ⏳ Build authentication system
6. ⏳ Create views and templates
7. ⏳ Build dashboards

---

## Commands to Run

```bash
# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access admin panel
http://localhost:8000/admin
```
