import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_care.settings')
django.setup()
from accounts.models import User
from django.conf import settings

print('MEDIA_ROOT:', settings.MEDIA_ROOT)
print('MEDIA_URL:', settings.MEDIA_URL)
print('DEFAULT_FILE_STORAGE:', getattr(settings, 'DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage'))
print()

users = User.objects.exclude(profile_picture='').exclude(profile_picture=None)
print(f'Users with profile_picture set: {users.count()}')
for u in users:
    path = os.path.join(settings.MEDIA_ROOT, str(u.profile_picture))
    exists = os.path.exists(path)
    try:
        url = u.profile_picture.url
    except Exception as e:
        url = f'ERROR: {e}'
    print(f'  {u.username} | field={u.profile_picture} | url={url} | file_exists={exists}')
