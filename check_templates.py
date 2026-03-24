import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_care.settings')
django.setup()
from django.template.loader import get_template
templates = [
    'accounts/profile.html',
    'accounts/profile_counselor.html',
    'accounts/student_profile.html',
    'accounts/student_profile_edit.html',
    'admin/manage_users.html',
    'admin/teachers_list.html',
    'admin/teacher_dashboard_view.html',
    'counselor_base.html',
    'base.html',
]
for t in templates:
    try:
        get_template(t)
        print('OK: ' + t)
    except Exception as e:
        print('ERROR: ' + t + ' -> ' + str(e))
