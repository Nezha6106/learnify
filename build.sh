#!/usr/bin/env bash
set -e

python -m pip install -r requirements.txt
mkdir -p logs
python manage.py collectstatic --no-input
python manage.py migrate

# Add this line right here!
python manage.py populate_courses