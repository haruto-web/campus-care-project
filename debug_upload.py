import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_care.settings')
django.setup()

from accounts.models import User
from django.core.files.base import ContentFile

# Get the first admin/teacher/counselor user
user = User.objects.filter(role__in=['admin','teacher','counselor']).first()
if not user:
    user = User.objects.first()

print(f'Testing with user: {user.username} ({user.role})')
print(f'Current profile_picture: "{user.profile_picture}"')

# Simulate uploading a small test image (1x1 red pixel PNG)
import base64
png_1x1 = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=='
)
test_file = ContentFile(png_1x1, name='test_profile.png')

try:
    user.profile_picture = test_file
    user.save(update_fields=['profile_picture'])
    print(f'Save OK. profile_picture field = "{user.profile_picture}"')
    
    # Re-fetch from DB
    user.refresh_from_db()
    print(f'After refresh_from_db: "{user.profile_picture}"')
    
    if user.profile_picture:
        full_path = os.path.join('D:\\Campus Care_Project\\campus-care-project\\media', str(user.profile_picture))
        print(f'File path: {full_path}')
        print(f'File exists on disk: {os.path.exists(full_path)}')
        print(f'URL: {user.profile_picture.url}')
    else:
        print('ERROR: profile_picture is empty after save!')
except Exception as e:
    import traceback
    print(f'EXCEPTION: {e}')
    traceback.print_exc()
