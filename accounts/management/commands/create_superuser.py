from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create a superuser for testing'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@campuscare.com', password='admin123',
                role='admin', first_name='Admin', last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Default admin created.'))
        if not User.objects.filter(email='venandrewmirasol@gmail.com').exists():
            u = User.objects.create_superuser(
                username='venandrew', email='venandrewmirasol@gmail.com',
                password='@Admin1234', role='admin',
                first_name='Ven Andrew', last_name='Mirasol', profile_completed=True
            )
            u.admin_role = 'superadmin'
            u.save(update_fields=['admin_role'])
            self.stdout.write(self.style.SUCCESS('Superadmin venandrew created.'))
        if not User.objects.filter(email='mslmandapat@tip.edu.ph').exists():
            u = User.objects.create_superuser(
                username='mslmandapat', email='mslmandapat@tip.edu.ph',
                password='@Admin1234', role='admin',
                first_name='Msl', last_name='Mandapat', profile_completed=True
            )
            u.admin_role = 'superadmin'
            u.save(update_fields=['admin_role'])
            self.stdout.write(self.style.SUCCESS('Superadmin mslmandapat created.'))
        else:
            self.stdout.write(self.style.WARNING('Accounts already exist.'))
