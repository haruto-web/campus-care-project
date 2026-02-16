# Counselor Features - Testing Guide

## Prerequisites

Before testing, ensure you have:
1. A counselor user account (create via Django admin if needed)
2. Some students with risk assessments in the database
3. Some existing alerts in the system
4. Test data for students (grades, attendance, wellness check-ins)

---

## Test 1: Login and Dashboard

### Steps:
1. Navigate to `/login/`
2. Login with counselor credentials
3. Verify redirect to counselor dashboard

### Expected Results:
- ✅ Dashboard displays at-risk students overview
- ✅ Quick stats show: high risk count, medium risk count
- ✅ Unread alerts count displayed
- ✅ Pending interventions count displayed
- ✅ Upcoming interventions list (if any)
- ✅ Navbar shows: Dashboard, At-Risk Students, Interventions, Alerts

---

## Test 2: At-Risk Students List

### Steps:
1. Click "At-Risk Students" in navbar
2. Verify page loads with student cards
3. Test risk level filter:
   - Select "High Risk" → Submit
   - Verify only high-risk students shown
4. Test search:
   - Enter student name → Submit
   - Verify filtered results
5. Click "View Profile" on a student card
6. Verify student profile loads

### Expected Results:
- ✅ All students with risk assessments displayed
- ✅ Student cards show: photo, name, email, risk badge, stats
- ✅ Risk badges are color-coded (red=high, yellow=medium, green=low)
- ✅ Filter by risk level works
- ✅ Search by name/email works
- ✅ "View Profile" button navigates to student profile
- ✅ "Create Intervention" button visible on each card

---

## Test 3: Create Intervention (from At-Risk Students)

### Steps:
1. From At-Risk Students list
2. Click "Create Intervention" on a student card
3. Verify form loads with student pre-selected
4. Fill form:
   - Intervention Type: "Counseling Session"
   - Description: "Initial wellness check-in meeting"
   - Scheduled Date: Select future date/time
   - Status: "Scheduled"
   - Notes: "Prepare wellness assessment"
5. Click "Create Intervention"

### Expected Results:
- ✅ Form displays with all fields
- ✅ Student field is pre-filled
- ✅ All intervention types available in dropdown
- ✅ Date/time picker works
- ✅ Success message appears
- ✅ Redirects to interventions list
- ✅ New intervention appears in list

---

## Test 4: Interventions List

### Steps:
1. Click "Interventions" in navbar
2. Verify interventions table displays
3. Test status filter:
   - Select "Scheduled" → Submit
   - Verify only scheduled interventions shown
4. Click student name link
5. Verify navigates to student profile
6. Click "Edit" button on an intervention

### Expected Results:
- ✅ All interventions displayed in table
- ✅ Columns show: Student, Type, Date, Status, Counselor, Actions
- ✅ Status badges are color-coded
- ✅ Filter by status works
- ✅ Student name links to profile
- ✅ "Create Intervention" button at top
- ✅ "Edit" button navigates to update form

---

## Test 5: Update Intervention

### Steps:
1. From interventions list, click "Edit" on an intervention
2. Verify form loads with existing data
3. Update fields:
   - Status: Change to "Completed"
   - Outcome: "Student showed improvement in stress management"
4. Click "Update Intervention"

### Expected Results:
- ✅ Form displays with pre-filled data
- ✅ Student info shown at top
- ✅ All fields editable
- ✅ Success message appears
- ✅ Redirects to interventions list
- ✅ Updated intervention shows new status
- ✅ Status badge updated to "Completed" (green)

---

## Test 6: Create Intervention (from Interventions List)

### Steps:
1. From interventions list
2. Click "Create Intervention" button
3. Fill form:
   - Student: Select from dropdown
   - Intervention Type: "Tutoring"
   - Description: "Math tutoring session"
   - Scheduled Date: Select date/time
   - Status: "Scheduled"
4. Click "Create Intervention"

### Expected Results:
- ✅ Form displays with empty fields
- ✅ All students available in dropdown
- ✅ Form validates required fields
- ✅ Success message appears
- ✅ New intervention appears in list

---

## Test 7: Alerts List

### Steps:
1. Click "Alerts" in navbar
2. Verify alerts displayed
3. Test alert type filter:
   - Select "High Risk Student" → Submit
   - Verify only high-risk alerts shown
4. Test show resolved toggle:
   - Select "Yes" → Submit
   - Verify resolved alerts appear
5. Click "View Student" on an alert
6. Verify navigates to student profile

### Expected Results:
- ✅ All unresolved alerts displayed by default
- ✅ Alert cards show: icon, type, message, student, timestamp
- ✅ "New" badge on unread alerts
- ✅ Filter by type works
- ✅ Show resolved toggle works
- ✅ Icons are type-specific and color-coded
- ✅ Student name links to profile

---

## Test 8: Mark Alert as Read

### Steps:
1. From alerts list
2. Find an unread alert (has "New" badge)
3. Click "Mark Read" button
4. Verify page reloads

### Expected Results:
- ✅ Success message appears
- ✅ "New" badge removed from alert
- ✅ Alert still visible in list
- ✅ "Mark Read" button no longer shown

---

## Test 9: Resolve Alert

### Steps:
1. From alerts list
2. Find an unresolved alert
3. Click "Resolve" button
4. Verify page reloads

### Expected Results:
- ✅ Success message appears
- ✅ Alert removed from default view
- ✅ "Resolved" badge appears if show resolved is enabled
- ✅ Alert marked as both read and resolved

---

## Test 10: Student Profile View (Counselor Access)

### Steps:
1. Navigate to a student profile (from at-risk list or alert)
2. Verify all sections display:
   - Student info and photo
   - Risk level indicator
   - Academic performance
   - Attendance stats
   - Recent attendance records
   - Wellness check-ins
   - Teacher concerns
   - Interventions
3. Click "Create Intervention" button (if visible)

### Expected Results:
- ✅ All student data displayed
- ✅ Risk level badge color-coded
- ✅ GPA, attendance rate, missing assignments shown
- ✅ Recent attendance table (last 10)
- ✅ Wellness check-ins table (last 5)
- ✅ Teacher concerns table (last 10)
- ✅ Interventions table (last 10)
- ✅ All data accurate and up-to-date

---

## Test 11: Navigation Flow

### Steps:
1. Start at Dashboard
2. Click "At-Risk Students" → verify page loads
3. Click "Interventions" → verify page loads
4. Click "Alerts" → verify page loads
5. Click "Dashboard" → verify returns to dashboard
6. Click profile dropdown → "Profile" → verify loads
7. Click "Logout" → verify logs out

### Expected Results:
- ✅ All navbar links work
- ✅ No broken links
- ✅ Smooth navigation between pages
- ✅ Active page highlighted in navbar
- ✅ Profile dropdown works
- ✅ Logout works correctly

---

## Test 12: Permission Checks

### Steps:
1. Logout from counselor account
2. Login as a student
3. Try to access counselor URLs directly:
   - `/wellness/at-risk-students/`
   - `/wellness/interventions/`
   - `/wellness/alerts/`

### Expected Results:
- ✅ "Permission denied" error message
- ✅ Redirects to dashboard
- ✅ Student cannot access counselor features
- ✅ Counselor navbar items not visible to students

---

## Test 13: Create Intervention from Student Profile

### Steps:
1. Login as counselor
2. Navigate to a student profile
3. Look for "Create Intervention" button/link
4. Click it
5. Verify form loads with student pre-selected

### Expected Results:
- ✅ Button/link visible on student profile
- ✅ Navigates to create intervention form
- ✅ Student field pre-filled
- ✅ Can create intervention successfully

---

## Test 14: Filter Combinations

### Steps:
1. **At-Risk Students:**
   - Apply risk filter + search together
   - Verify both filters work simultaneously
2. **Interventions:**
   - Filter by status
   - Verify correct interventions shown
3. **Alerts:**
   - Filter by type + show resolved
   - Verify both filters work together

### Expected Results:
- ✅ Multiple filters work together
- ✅ Results update correctly
- ✅ No errors when combining filters
- ✅ Clear filters returns to full list

---

## Test 15: Edge Cases

### Test Empty States:
1. Filter to show no results
2. Verify "No items found" message displays

### Test Long Text:
1. Create intervention with very long description
2. Verify text displays properly (no overflow)

### Test Date/Time:
1. Create intervention with past date
2. Verify it still saves (no validation error)

### Expected Results:
- ✅ Empty states handled gracefully
- ✅ Long text doesn't break layout
- ✅ Date validation works as expected
- ✅ No JavaScript errors in console

---

## Common Issues & Solutions

### Issue: No students in At-Risk Students list
**Solution:** Create risk assessments via Django admin or run risk calculation script

### Issue: No alerts showing
**Solution:** Alerts need to be created manually or via automation (not yet implemented)

### Issue: Permission denied for counselor
**Solution:** Verify user role is set to "counselor" in database

### Issue: Student not in dropdown
**Solution:** Verify student role is set to "student" in database

### Issue: Form validation errors
**Solution:** Check all required fields are filled correctly

---

## Success Criteria

All tests should pass with:
- ✅ No error messages (except expected permission denials)
- ✅ All pages load correctly
- ✅ All forms submit successfully
- ✅ All filters work as expected
- ✅ All navigation links functional
- ✅ Data displays accurately
- ✅ Permission checks work correctly
- ✅ UI is responsive and user-friendly

---

## Reporting Issues

If you find any issues during testing:
1. Note the exact steps to reproduce
2. Screenshot the error (if any)
3. Check browser console for JavaScript errors
4. Check Django logs for server errors
5. Document expected vs actual behavior

---

## Next Steps After Testing

Once all tests pass:
1. ✅ Mark counselor features as complete
2. Move to student features implementation
3. Consider adding automated tests (unit tests, integration tests)
4. Plan for automated alert generation
5. Design reports and analytics features

---

**Happy Testing!** 🧪
