# Counselor Features Implementation Guide

## Overview
This guide documents the complete implementation of counselor features in Campus Care LMS, enabling counselors to monitor at-risk students, create interventions, and manage alerts.

**Date:** February 15, 2026  
**Status:** 90% Complete  
**Remaining:** Profile page, Reports/Analytics

---

## Features Implemented

### 1. At-Risk Students List
**URL:** `/wellness/at-risk-students/`  
**Template:** `templates/wellness/at_risk_students.html`  
**View:** `wellness.views.at_risk_students_list`

**Features:**
- View all students with risk assessments
- Filter by risk level (High, Medium, Low)
- Search by student name or email
- Display student cards with:
  - Profile picture
  - Risk level badge (color-coded)
  - Risk score
  - GPA, Attendance rate, Missing assignments
- Quick actions:
  - View student profile
  - Create intervention

**Access:** Counselors and Admins only

---

### 2. Create Intervention
**URL:** `/wellness/intervention/create/`  
**URL (for specific student):** `/wellness/intervention/create/<student_id>/`  
**Template:** `templates/wellness/create_intervention.html`  
**View:** `wellness.views.create_intervention`  
**Form:** `wellness.forms.InterventionForm`

**Fields:**
- Student (dropdown)
- Intervention Type (counseling, tutoring, parent meeting, academic plan, other)
- Description (purpose and goals)
- Scheduled Date & Time
- Status (scheduled, completed, cancelled)
- Notes (optional)
- Outcome (optional - for after completion)

**Features:**
- Pre-fill student if coming from student profile
- All students available in dropdown
- Validation for required fields
- Success message on creation
- Redirect to interventions list

**Access:** Counselors and Admins only

---

### 3. Interventions List
**URL:** `/wellness/interventions/`  
**Template:** `templates/wellness/interventions_list.html`  
**View:** `wellness.views.interventions_list`

**Features:**
- View all interventions in table format
- Filter by status (Scheduled, Completed, Cancelled)
- Display columns:
  - Student name (clickable to profile)
  - Intervention type (badge)
  - Scheduled date & time
  - Status (color-coded badge)
  - Counselor name
  - Edit action button
- Create new intervention button
- Sorted by scheduled date (newest first)

**Access:** Counselors and Admins only

---

### 4. Update Intervention
**URL:** `/wellness/intervention/<intervention_id>/update/`  
**Template:** `templates/wellness/update_intervention.html`  
**View:** `wellness.views.update_intervention`  
**Form:** `wellness.forms.InterventionForm`

**Features:**
- Edit existing intervention
- All fields editable
- Display creation date and student info
- Update status (mark as completed/cancelled)
- Add outcome after completion
- Success message on update
- Redirect to interventions list

**Access:** Counselors and Admins only

---

### 5. Alerts & Notifications
**URL:** `/wellness/alerts/`  
**Template:** `templates/wellness/alerts_list.html`  
**View:** `wellness.views.alerts_list`

**Features:**
- View all system alerts
- Filter by alert type:
  - High Risk Student
  - Missing Assignments
  - Low Attendance
  - Wellness Concern
  - Teacher Concern
- Toggle show/hide resolved alerts
- Alert cards display:
  - Icon (type-specific)
  - Alert type and message
  - Student name (clickable)
  - Timestamp
  - Status badges (New, Resolved)
- Actions:
  - Mark as read
  - Resolve alert
  - View student profile
- Sorted by creation date (newest first)

**Alert Types:**
1. **High Risk** - Student moved to high risk level
2. **Missing Assignments** - Multiple assignments not submitted
3. **Low Attendance** - Attendance dropped below threshold
4. **Wellness Concern** - Wellness check-in shows distress
5. **Teacher Concern** - Teacher submitted a concern

**Access:** Counselors and Admins only

---

### 6. Mark Alert as Read
**URL:** `/wellness/alert/<alert_id>/read/`  
**View:** `wellness.views.mark_alert_read`

**Features:**
- Mark alert as read (removes "New" badge)
- Success message
- Redirect back to alerts list

**Access:** Counselors and Admins only

---

### 7. Resolve Alert
**URL:** `/wellness/alert/<alert_id>/resolve/`  
**View:** `wellness.views.resolve_alert`

**Features:**
- Mark alert as resolved
- Automatically marks as read
- Success message
- Redirect back to alerts list

**Access:** Counselors and Admins only

---

### 8. Student Profile View (Counselor Access)
**URL:** `/student/<student_id>/`  
**Template:** `templates/accounts/student_profile.html`  
**View:** `accounts.views.student_profile_view`

**Features:**
- Counselors can view comprehensive student profiles
- Same view as teachers
- Displays:
  - Student info and photo
  - Risk level indicator
  - Academic performance (GPA, missing assignments)
  - Attendance rate and recent records
  - Wellness check-ins
  - Teacher concerns
  - Interventions history
- Quick action: Create intervention from profile

**Access:** Teachers, Counselors, and Admins

---

## Navigation

### Counselor Navbar Links (in base.html):
1. **Dashboard** - `/dashboard/`
2. **At-Risk Students** - `/wellness/at-risk-students/`
3. **Interventions** - `/wellness/interventions/`
4. **Alerts** - `/wellness/alerts/`
5. **Profile** - `/profile/` (dropdown)

---

## Database Models Used

### Intervention Model
```python
class Intervention(models.Model):
    student = ForeignKey(User)
    counselor = ForeignKey(User)
    intervention_type = CharField (counseling, tutoring, parent_meeting, academic_plan, other)
    description = TextField
    scheduled_date = DateTimeField
    status = CharField (scheduled, completed, cancelled)
    notes = TextField (optional)
    outcome = TextField (optional)
    created_at = DateTimeField (auto)
    updated_at = DateTimeField (auto)
```

### Alert Model
```python
class Alert(models.Model):
    student = ForeignKey(User)
    alert_type = CharField (high_risk, missing_assignments, low_attendance, wellness_concern, teacher_concern)
    message = TextField
    created_at = DateTimeField (auto)
    is_read = BooleanField (default=False)
    resolved = BooleanField (default=False)
```

### RiskAssessment Model
```python
class RiskAssessment(models.Model):
    student = ForeignKey(User)
    date = DateField (auto)
    risk_level = CharField (low, medium, high)
    risk_score = DecimalField
    gpa = DecimalField (optional)
    attendance_rate = DecimalField (optional)
    missing_assignments = IntegerField
    notes = TextField (optional)
```

---

## URLs Configuration

### wellness/urls.py
```python
# Counselor - At-Risk Students
path('at-risk-students/', views.at_risk_students_list, name='at_risk_students'),

# Counselor - Interventions
path('intervention/create/', views.create_intervention, name='create_intervention'),
path('intervention/create/<int:student_id>/', views.create_intervention, name='create_intervention_for_student'),
path('interventions/', views.interventions_list, name='interventions_list'),
path('intervention/<int:intervention_id>/update/', views.update_intervention, name='update_intervention'),

# Counselor - Alerts
path('alerts/', views.alerts_list, name='alerts_list'),
path('alert/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
path('alert/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
```

---

## Permission Checks

All counselor views include permission checks:
```python
if request.user.role not in ['counselor', 'admin']:
    messages.error(request, 'Permission denied.')
    return redirect('dashboard')
```

---

## User Flow Examples

### Flow 1: Monitor At-Risk Students
1. Counselor logs in → Dashboard
2. Clicks "At-Risk Students" in navbar
3. Views list of students with risk assessments
4. Filters by "High Risk"
5. Clicks on student card to view profile
6. Reviews student details, concerns, wellness data
7. Clicks "Create Intervention" button

### Flow 2: Create and Manage Intervention
1. From student profile or interventions list
2. Clicks "Create Intervention"
3. Fills form:
   - Selects student
   - Chooses intervention type (e.g., Counseling Session)
   - Describes purpose
   - Sets scheduled date/time
   - Sets status to "Scheduled"
4. Submits form
5. Views intervention in list
6. After meeting, clicks "Edit"
7. Updates status to "Completed"
8. Adds outcome notes
9. Saves changes

### Flow 3: Manage Alerts
1. Counselor clicks "Alerts" in navbar
2. Views unresolved alerts
3. Filters by "High Risk Student"
4. Reviews alert details
5. Clicks "View Student" to see profile
6. Takes action (creates intervention, contacts teacher)
7. Returns to alerts
8. Clicks "Resolve" to mark as handled
9. Alert moves to resolved status

---

## Testing Checklist

### At-Risk Students
- [ ] List displays all students with risk assessments
- [ ] Filter by risk level works
- [ ] Search by name/email works
- [ ] Student cards show correct data
- [ ] Risk level badges are color-coded correctly
- [ ] Links to student profile work
- [ ] Create intervention button works

### Interventions
- [ ] Create intervention form displays
- [ ] All fields validate correctly
- [ ] Intervention saves to database
- [ ] List displays all interventions
- [ ] Filter by status works
- [ ] Edit intervention loads correct data
- [ ] Update saves changes
- [ ] Status badges display correctly

### Alerts
- [ ] Alerts list displays all alerts
- [ ] Filter by type works
- [ ] Show/hide resolved toggle works
- [ ] Mark as read updates status
- [ ] Resolve alert works
- [ ] Alert icons display correctly
- [ ] Links to student profile work

---

## What's Still Needed

### 1. Counselor Profile Page (⏳)
- Create dedicated profile page for counselors
- Similar to teacher profile
- View and edit personal information
- Upload profile picture

### 2. Reports & Analytics (⏳)
- System-wide statistics
- Intervention effectiveness tracking
- Risk level trends over time
- Student outcome reports

### 3. Automated Alert Generation (⏳)
- Django signals to auto-create alerts
- Trigger on risk level changes
- Trigger on wellness check-in concerns
- Trigger on attendance/grade drops

---

## Files Created/Modified

### New Files:
1. `templates/wellness/at_risk_students.html`
2. `templates/wellness/create_intervention.html`
3. `templates/wellness/interventions_list.html`
4. `templates/wellness/update_intervention.html`
5. `templates/wellness/alerts_list.html`

### Modified Files:
1. `wellness/views.py` - Added 7 new views
2. `wellness/forms.py` - Added InterventionForm
3. `wellness/urls.py` - Added 7 new URL patterns
4. `templates/base.html` - Updated counselor navigation
5. `README.md` - Updated progress tracking

---

## Success Metrics

✅ **Completed:**
- 7 new views implemented
- 5 new templates created
- 1 new form created
- 7 new URL patterns
- Navigation updated
- Permission checks in place
- All CRUD operations for interventions
- Alert management system
- At-risk student monitoring

✅ **Progress:**
- Counselor features: 90% complete
- Overall project: 80% complete

---

## Next Steps

1. **Test all counselor features** with real data
2. **Create counselor profile page** (similar to teacher)
3. **Implement automated alert generation** using Django signals
4. **Add reports and analytics** dashboard
5. **Move to student features** (assignment submission, wellness check-in)

---

## Notes

- All counselor views are accessible to admins as well
- Student profile view is shared between teachers and counselors
- Interventions can be created from multiple entry points
- Alerts system is ready but needs automation
- Risk assessments are calculated but need scheduling

---

**Implementation Complete!** 🎉

Counselors now have a comprehensive system to:
- Monitor at-risk students
- Create and manage interventions
- Track alerts and notifications
- View detailed student profiles
- Take proactive support actions
