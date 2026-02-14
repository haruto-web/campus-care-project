# Campus Care - Admin Panel Testing Guide

## ✅ Setup Complete!

### Superuser Created
- **Username:** admin
- **Password:** admin123
- **Email:** admin@campuscare.com

### Sample Test Accounts

**Teacher:**
- Username: teacher1
- Password: teacher123

**Counselor:**
- Username: counselor1
- Password: counselor123

**Students:**
- student1 / student123
- student2 / student123
- student3 / student123
- student4 / student123
- student5 / student123

### Sample Data Created
- 2 Classes (CS101, CS201)
- 2 Assignments
- 5 Students enrolled in classes

---

## How to Test Admin Panel

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Access Admin Panel
Open browser: http://localhost:8000/admin

### 3. Login
- Username: admin
- Password: admin123

### 4. Test These Features

**Users Management:**
- View all users (students, teachers, counselors)
- Filter by role
- Edit user profiles

**Classes:**
- View CS101 and CS201
- See enrolled students
- Check teacher assignments

**Assignments:**
- View created assignments
- Check due dates and points

**Wellness (Campus Care):**
- Create wellness check-ins
- Add risk assessments
- Submit teacher concerns
- Create interventions
- Generate alerts

**Academics:**
- Mark attendance
- Enter grades
- View submissions

---

## Next Steps After Testing

1. ✅ Verify all models appear in admin
2. ✅ Test creating/editing records
3. ⏳ Build authentication views (login/logout)
4. ⏳ Create role-based dashboards
5. ⏳ Build student/teacher interfaces

---

## Admin Panel URL
http://localhost:8000/admin
