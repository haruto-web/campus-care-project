"""
Quick setup script for Google OAuth
Run this after adding credentials to .env file
"""

from django.contrib.sites.models import Site

def setup_site():
    site = Site.objects.get_current()
    site.domain = 'localhost:8000'
    site.name = 'BrightTrack LMS'
    site.save()
    print(f"✅ Site configured: {site.name} ({site.domain})")
    print(f"✅ Site ID: {site.id}")
    print("\nNext steps:")
    print("1. Add GOOGLE_CLIENT_ID to .env")
    print("2. Add GOOGLE_CLIENT_SECRET to .env")
    print("3. Run: python manage.py runserver")
    print("4. Visit: http://localhost:8000/login/")

if __name__ == '__main__':
    setup_site()
