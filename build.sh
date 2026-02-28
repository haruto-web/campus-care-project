#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py configure_site
python manage.py create_superuser
python manage.py create_dummy_students
