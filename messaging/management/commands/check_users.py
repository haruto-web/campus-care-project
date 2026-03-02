from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Check existing users and create test users for messaging'

    def handle(self, *args, **options):
        self.stdout.write("Checking existing users...")
        
        # Count users by role
        for role, _ in User.ROLE_CHOICES:
            count = User.objects.filter(role=role).count()
            self.stdout.write(f"{role.capitalize()}s: {count}")
        
        total_users = User.objects.count()
        self.stdout.write(f"Total users: {total_users}")
        
        if total_users < 5:  # Create some test users if we don't have enough
            self.stdout.write("Creating test users...")
            
            # Create admin if doesn't exist
            if not User.objects.filter(role='admin').exists():
                User.objects.create_user(
                    username='admin',
                    email='admin@school.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    role='admin'
                )
                self.stdout.write("Created admin user")
            
            # Create counselor if doesn't exist
            if not User.objects.filter(role='counselor').exists():
                User.objects.create_user(
                    username='counselor',
                    email='counselor@school.com',
                    password='counselor123',
                    first_name='Sarah',
                    last_name='Johnson',
                    role='counselor'
                )
                self.stdout.write("Created counselor user")
            
            # Create teacher if doesn't exist
            if not User.objects.filter(role='teacher').exists():
                User.objects.create_user(
                    username='teacher',
                    email='teacher@school.com',
                    password='teacher123',
                    first_name='John',
                    last_name='Smith',
                    role='teacher',
                    section='Apple'
                )
                self.stdout.write("Created teacher user")
            
            # Create student if doesn't exist
            if not User.objects.filter(role='student').exists():
                User.objects.create_user(
                    username='student',
                    email='student@school.com',
                    password='student123',
                    first_name='Alice',
                    last_name='Brown',
                    role='student',
                    year_level='7',
                    section='Apple'
                )
                self.stdout.write("Created student user")
        
        self.stdout.write(self.style.SUCCESS("User check complete!"))