from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create a superuser for testing'

    def handle(self, *args, **kwargs):
        # Force-ensure superadmin accounts exist and have correct passwords
        accounts = [
            ('admin', 'admin@campuscare.com', 'admin123', 'Admin', 'User', ''),
            ('johnaldrich', 'mjapayawal@tip.edu.ph', '@Admin1234', 'John Aldrich', 'Payawal', 'superadmin'),
            ('mvamirasol', 'mvamirasol@tip.edu.ph', '@Admin1234', 'Ven Andrew', 'Mirasol', 'superadmin'),
            ('mrmantig', 'mrmantig@tip.edu.ph', '@Admin1234', 'Rome Michael', 'Antig', 'superadmin'),
            ('mslmandapat', 'mslmandapat@tip.edu.ph', '@Admin1234', 'Msl', 'Mandapat', 'superadmin'),
        ]
        for username, email, password, fn, ln, admin_role in accounts:
            u, created = User.objects.get_or_create(
                email=email,
                defaults=dict(username=username, first_name=fn, last_name=ln,
                              role='admin', is_staff=True, is_superuser=True,
                              profile_completed=True)
            )
            u.set_password(password)
            u.is_staff = True
            u.is_superuser = True
            u.role = 'admin'
            u.profile_completed = True
            if admin_role:
                u.admin_role = admin_role
            u.save()
            self.stdout.write(self.style.SUCCESS(f'{'Created' if created else 'Updated'}: {email}'))
