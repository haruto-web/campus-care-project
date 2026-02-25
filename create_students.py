import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_care.settings')
django.setup()

from accounts.models import User
from wellness.models import RiskAssessment, WellnessCheckIn
from django.contrib.auth.hashers import make_password

sections = ['Apple', 'Banana', 'Grapes']
genders = ['male', 'female']
year_levels = [7, 8, 9, 10]

print("Creating 50 students...")

# Create 50 students
for i in range(1, 51):
    username = f"student{i}"
    email = f"student{i}@gmail.com"
    section = random.choice(sections)
    gender = random.choice(genders)
    year_level = random.choice(year_levels)
    
    user = User.objects.create(
        username=username,
        email=email,
        first_name=f"Student{i}",
        last_name="User",
        role='student',
        section=section,
        gender=gender,
        year_level=year_level,
        password=make_password('123456')
    )
    print(f"Created {username} - {section} - {gender} - Grade {year_level}")

print("\nCreating risk assessments...")

# Get all students
students = list(User.objects.filter(role='student'))

# 10 medium risk students
for i in range(10):
    student = students[i]
    RiskAssessment.objects.create(
        student=student,
        risk_level='medium',
        risk_score=50.0,
        gpa=2.8,
        attendance_rate=78.0,
        missing_assignments=2
    )
    print(f"Created MEDIUM risk for {student.username}")

# 10 high risk students
for i in range(10, 20):
    student = students[i]
    RiskAssessment.objects.create(
        student=student,
        risk_level='high',
        risk_score=80.0,
        gpa=2.0,
        attendance_rate=65.0,
        missing_assignments=5
    )
    print(f"Created HIGH risk for {student.username}")

print("\nCreating wellness check-ins with critical severity...")

# 5 students with critical wellness check-ins
for i in range(20, 25):
    student = students[i]
    WellnessCheckIn.objects.create(
        student=student,
        stress_level=5,
        motivation_level=1,
        workload_level=5,
        sleep_quality=1,
        need_help=True,
        comments="Feeling overwhelmed and stressed"
    )
    
    # Create high risk assessment for these students
    RiskAssessment.objects.create(
        student=student,
        risk_level='high',
        risk_score=90.0,
        gpa=1.8,
        attendance_rate=60.0,
        missing_assignments=7
    )
    print(f"Created CRITICAL wellness check-in for {student.username}")

print("\n✅ All students created successfully!")
print(f"Total students: {User.objects.filter(role='student').count()}")
print(f"Medium risk: {RiskAssessment.objects.filter(risk_level='medium').count()}")
print(f"High risk: {RiskAssessment.objects.filter(risk_level='high').count()}")
print(f"Wellness check-ins: {WellnessCheckIn.objects.count()}")
