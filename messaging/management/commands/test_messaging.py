from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from messaging.models import Conversation, Message
from messaging.content_filter import contains_inappropriate_content
from messaging.views import ALLOWED_RECIPIENTS

User = get_user_model()

class Command(BaseCommand):
    help = 'Test all messaging functions'

    def handle(self, *args, **options):
        self.stdout.write("Testing messaging system...")
        
        # Test 1: Check users exist
        self.stdout.write("\n1. Checking users...")
        students = User.objects.filter(role='student')
        teachers = User.objects.filter(role='teacher')
        counselors = User.objects.filter(role='counselor')
        admins = User.objects.filter(role='admin')
        
        self.stdout.write(f"Students: {students.count()}")
        self.stdout.write(f"Teachers: {teachers.count()}")
        self.stdout.write(f"Counselors: {counselors.count()}")
        self.stdout.write(f"Admins: {admins.count()}")
        
        # Test 2: Check role permissions
        self.stdout.write("\n2. Checking role permissions...")
        for role, allowed in ALLOWED_RECIPIENTS.items():
            self.stdout.write(f"{role} can message: {', '.join(allowed)}")
        
        # Test 3: Test content filter
        self.stdout.write("\n3. Testing content filter...")
        test_messages = [
            "Hello, how are you?",  # Clean
            "You are gago",  # Inappropriate
            "putangina mo",  # Inappropriate
            "This is a normal message",  # Clean
            "bobo ka",  # Inappropriate
        ]
        
        for msg in test_messages:
            is_bad, words = contains_inappropriate_content(msg)
            status = "BLOCKED" if is_bad else "ALLOWED"
            self.stdout.write(f"'{msg}' -> {status}")
            if words:
                self.stdout.write(f"  Found: {', '.join(words)}")
        
        # Test 4: Check conversation creation
        self.stdout.write("\n4. Testing conversation creation...")
        if students.exists() and teachers.exists():
            student = students.first()
            teacher = teachers.first()
            
            # Create test conversation
            conv = Conversation.objects.create()
            conv.participants.add(student, teacher)
            
            # Create test message
            Message.objects.create(
                conversation=conv,
                sender=student,
                body="Test message from student"
            )
            
            self.stdout.write(f"Created conversation between {student.get_full_name()} and {teacher.get_full_name()}")
            self.stdout.write(f"Messages in conversation: {conv.messages.count()}")
            
            # Clean up
            conv.delete()
        
        # Test 5: Check user data completeness
        self.stdout.write("\n5. Checking user data completeness...")
        for user in User.objects.all()[:5]:  # Check first 5 users
            missing_data = []
            if not user.first_name:
                missing_data.append("first_name")
            if not user.last_name:
                missing_data.append("last_name")
            if user.role == 'student' and not user.year_level:
                missing_data.append("year_level")
            if user.role == 'student' and not user.section:
                missing_data.append("section")
            
            if missing_data:
                self.stdout.write(f"User {user.username} missing: {', '.join(missing_data)}")
            else:
                self.stdout.write(f"User {user.get_full_name()} ({user.role}) - Complete")
        
        self.stdout.write(self.style.SUCCESS("\nMessaging system test complete!"))