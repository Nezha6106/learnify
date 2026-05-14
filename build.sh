#!/usr/bin/env bash
set -e

python -m pip install -r requirements.txt
mkdir -p logs
python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create a superuser for the live server
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@admin.com
export DJANGO_SUPERUSER_PASSWORD=adminpassword123
python manage.py createsuperuser --noinput || true

# Add this line right here!
python manage.py populate_courses