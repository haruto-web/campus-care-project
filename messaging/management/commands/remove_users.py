from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Remove all users except admins'

    def handle(self, *args, **options):
        # Count users before deletion
        total_before = User.objects.count()
        admins_count = User.objects.filter(role='admin').count()
        
        # Delete non-admin users
        deleted_count = User.objects.exclude(role='admin').delete()[0]
        
        self.stdout.write(f"Users before: {total_before}")
        self.stdout.write(f"Admins kept: {admins_count}")
        self.stdout.write(f"Users deleted: {deleted_count}")
        self.stdout.write(self.style.SUCCESS("Only admin users remain!"))