# Report Concerns Feature - Implementation Guide

## ✅ Feature Overview

Teachers can now report concerns about students who may need additional support. This is part of the Campus Care early intervention system.

---

## 🎯 How to Use

### **For Teachers:**

#### **1. Report a Concern**
1. Login as Teacher
2. Go to Dashboard → Click "Report Concern"
3. Select student (only your students shown)
4. Choose concern type:
   - Academic
   - Behavioral
   - Emotional
   - Attendance
5. Select severity: Low / Medium / High
6. Enter date observed
7. Provide detailed description
8. Submit

#### **2. View Your Concerns**
1. Dashboard → Click "View My Concerns"
2. See all submitted concerns
3. Click "View" to see details
4. Check resolution status

---

## 📋 Concern Types

### **Academic**
- Failing grades
- Missing assignments
- Difficulty understanding material
- Lack of participation

### **Behavioral**
- Disruptive behavior
- Conflicts with peers
- Inappropriate conduct
- Attitude changes

### **Emotional**
- Signs of stress/anxiety
- Withdrawal from activities
- Mood changes
- Emotional outbursts

### **Attendance**
- Frequent absences
- Chronic lateness
- Unexplained absences
- Pattern of missing specific classes

---

## 🚨 Severity Levels

### **Low**
- Minor issues
- Early signs
- Preventive flagging

### **Medium**
- Noticeable patterns
- Affecting performance
- Needs attention soon

### **High**
- Urgent intervention needed
- Significant impact
- Immediate counselor review

---

## 📁 Files Created

### Forms (wellness/forms.py)
- `TeacherConcernForm` - Report concern form

### Views (wellness/views.py)
- `create_concern` - Submit new concern
- `view_concerns` - View submitted concerns

### Templates
- `wellness/create_concern.html` - Concern form
- `wellness/view_concerns.html` - Concerns list

### URLs
- `/wellness/concern/create/` - Report concern
- `/wellness/concern/create/<student_id>/` - Report for specific student
- `/wellness/concerns/` - View concerns

---

## 🔄 Workflow

### Teacher Side:
1. Teacher observes concerning behavior
2. Reports concern with details
3. Can view all submitted concerns
4. Tracks resolution status

### Counselor Side (Future):
1. Receives concern notification
2. Reviews concern details
3. Creates intervention plan
4. Marks concern as resolved

---

## 🔒 Security

- Only teachers can report concerns
- Teachers only see their own students
- Students from teacher's classes only
- Concerns visible to counselors/admins
- Confidential information protected

---

## 💡 Best Practices

### **When to Report:**
- ✅ Significant behavior changes
- ✅ Academic performance drops
- ✅ Attendance issues
- ✅ Emotional distress signs
- ✅ Safety concerns

### **What to Include:**
- Specific observations
- Dates and times
- Frequency of behavior
- Impact on student
- Any interventions tried

### **What NOT to Include:**
- Personal opinions
- Unverified information
- Gossip or rumors
- Medical diagnoses
- Confidential family info

---

## 📊 Database Structure

### TeacherConcern Model:
- `student` - Student of concern
- `teacher` - Reporting teacher
- `concern_type` - Category
- `severity` - Level of concern
- `description` - Detailed notes
- `date_observed` - When noticed
- `created_at` - Submission time
- `resolved` - Status flag

---

## 🎨 UI Features

### Report Form:
- Student dropdown (filtered)
- Concern type selector
- Severity selector
- Date picker
- Text area for description
- Info alert about process

### View Concerns:
- Table with all concerns
- Color-coded severity badges
- Status indicators
- Expandable details
- Quick filters (future)

---

## 🧪 Testing Checklist

### Report Concern:
- [ ] Select student from dropdown
- [ ] Choose concern type
- [ ] Set severity level
- [ ] Enter date observed
- [ ] Write description
- [ ] Submit successfully
- [ ] Verify in database

### View Concerns:
- [ ] See all submitted concerns
- [ ] Expand concern details
- [ ] Check status badges
- [ ] Verify sorting (newest first)
- [ ] Empty state shows correctly

### Security:
- [ ] Non-teachers can't access
- [ ] Only teacher's students shown
- [ ] Can't report for other teachers' students
- [ ] Concerns private to teacher

---

## 🚀 Future Enhancements

### Planned Features:
1. **Email Notifications** - Alert counselors of high-severity concerns
2. **Concern History** - View all concerns for a student
3. **Follow-up Notes** - Add updates to existing concerns
4. **Bulk Actions** - Mark multiple as resolved
5. **Analytics** - Concern trends and patterns
6. **Student Profile Integration** - Link to student detail page

---

## 📈 Integration Points

### Current:
- Teacher Dashboard (Quick Actions)
- Student selection (from teacher's classes)

### Future:
- Student Profile Page (show concerns)
- Counselor Dashboard (concern alerts)
- Risk Assessment (factor in concerns)
- Intervention Planning (link concerns)

---

## ✅ Feature Complete!

**All 5 Teacher Features Now Implemented:**
1. ✅ Create Assignment
2. ✅ Mark Attendance
3. ✅ View Submissions
4. ✅ Grade Assignments
5. ✅ Report Concerns

---

**Last Updated:** February 14, 2026
**Status:** Complete and Ready for Testing
