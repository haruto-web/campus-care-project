from django.core.management.base import BaseCommand
from accounts.models import User
from academics.models import Class
import random

class Command(BaseCommand):
    help = 'Create 1000 students with different grade levels and sections'

    def handle(self, *args, **kwargs):
        grade_levels = [7, 8, 9, 10]
        sections = ['Apple', 'Banana', 'Grapes']
        
        # Find the highest existing student number
        existing_students = User.objects.filter(username__startswith='student').order_by('-id')
        start_num = 1
        if existing_students.exists():
            last_username = existing_students.first().username
            try:
                start_num = int(last_username.replace('student', '')) + 1
            except:
                start_num = 1
        
        created_count = 0
        
        for i in range(start_num, start_num + 1000):
            username = f'student{i}'
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                continue
            
            # Assign grade level (evenly distributed)
            grade_level = grade_levels[(i - start_num) % 4]
            
            # Assign section (50 students per section, then None for the rest)
            section_index = (i - start_num) // 50
            if section_index < 3:
                section = sections[section_index]
            else:
                section = None
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password='123456',
                first_name=f'Student{i}',
                last_name='',
                email=f'student{i}@example.com',
                role='student',
                year_level=grade_level,
                section=section,
                profile_completed=True
            )
            
            # Auto-enroll in section class if section is assigned
            if section:
                class_code = f'SEC-{section.upper()}'
                section_class = Class.objects.filter(code=class_code).first()
                if section_class:
                    section_class.students.add(user)
            
            created_count += 1
            
            if created_count % 100 == 0:
                self.stdout.write(f'Created {created_count} students...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} students'))
