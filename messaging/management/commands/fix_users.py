from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix user data issues'

    def handle(self, *args, **options):
        # Fix user with missing names
        user = User.objects.filter(username='CampusCare').first()
        if user and not user.first_name:
            user.first_name = 'Campus'
            user.last_name = 'Care Admin'
            user.save()
            self.stdout.write(f"Fixed user: {user.username}")
        
        self.stdout.write(self.style.SUCCESS("User data fixed!"))