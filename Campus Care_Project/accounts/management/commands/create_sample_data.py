from django.core.management.base import BaseCommand
from accounts.models import User
from academics.models import Class, Assignment
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **kwargs):
        # Create sample users
        teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@campuscare.com',
            password='teacher123',
            role='teacher',
            first_name='John',
            last_name='Smith'
        )
        
        counselor = User.objects.create_user(
            username='counselor1',
            email='counselor@campuscare.com',
            password='counselor123',
            role='counselor',
            first_name='Sarah',
            last_name='Johnson'
        )
        
        students = []
        for i in range(1, 6):
            student = User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@campuscare.com',
                password='student123',
                role='student',
                first_name=f'Student',
                last_name=f'Number{i}'
            )
            students.append(student)
        
        # Create sample classes
        class1 = Class.objects.create(
            name='Introduction to Python',
            code='CS101',
            description='Learn Python programming basics',
            teacher=teacher,
            semester='Fall 2024'
        )
        class1.students.set(students[:3])
        
        class2 = Class.objects.create(
            name='Web Development',
            code='CS201',
            description='Build web applications with Django',
            teacher=teacher,
            semester='Fall 2024'
        )
        class2.students.set(students[2:])
        
        # Create sample assignments
        Assignment.objects.create(
            class_obj=class1,
            title='Python Basics Assignment',
            description='Complete exercises 1-10',
            due_date=datetime.now() + timedelta(days=7),
            total_points=100
        )
        
        Assignment.objects.create(
            class_obj=class2,
            title='Build a Django App',
            description='Create a simple blog application',
            due_date=datetime.now() + timedelta(days=14),
            total_points=150
        )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('\nTest Accounts:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Teacher: teacher1 / teacher123')
        self.stdout.write('Counselor: counselor1 / counselor123')
        self.stdout.write('Students: student1-5 / student123')
