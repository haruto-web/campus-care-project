#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "from django.contrib.sites.models import Site; s=Site.objects.get_current(); s.domain='brighttrack-lms.onrender.com'; s.name='BrightTrack LMS'; s.save(); print('Site configured:', s.domain)"
python manage.py create_superuser
python manage.py create_dummy_students
