#!/usr/bin/env bash
# Deploy: Feb 28 2026
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py migrate sites || true
python manage.py configure_site || true
python manage.py create_superuser || true
python manage.py create_dummy_students || true
