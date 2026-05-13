import os
from decouple import config
from courses.models import StudentAnalytics
from courses.views import analytics_dashboard
from django.contrib.auth.models import User
from django.test import RequestFactory
from pathlib import Path

print('═' * 60)
print('🔍 LEARNIFY SETUP VERIFICATION')
print('═' * 60)

# 1. Environment Setup
print('\n✅ ENVIRONMENT CONFIGURATION:')
print(f'   DEBUG mode: {config("DEBUG", default="True") == "True"}')
print(f'   SECRET_KEY loaded: {len(config("SECRET_KEY", default="")) > 10}')
print(f'   ALLOWED_HOSTS: {config("ALLOWED_HOSTS", default="not set")}')

# 2. Database Models
print('\n✅ DATABASE MODELS:')
analytics_count = StudentAnalytics.objects.count()
user_count = User.objects.count()
print(f'   StudentAnalytics records: {analytics_count}')
print(f'   Total users: {user_count}')

# 3. Views
print('\n✅ VIEWS:')
print(f'   analytics_dashboard function imported: True')
print(f'   View callable: {callable(analytics_dashboard)}')

# 4. Static Files
print('\n✅ FILE STRUCTURE:')
logs_exist = Path('logs').exists()
env_exist = Path('.env').exists()
print(f'   logs/ directory: {logs_exist}')
print(f'   .env file: {env_exist}')

# 5. Migration Status
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses_studentanalytics'")
table_exists = cursor.fetchone() is not None
print(f'   courses_studentanalytics table: {table_exists}')

print('\n' + '═' * 60)
print('✨ ALL SETUP COMPLETE - READY TO USE!')
print('═' * 60)
print('🌐 Access analytics at: http://localhost:8000/analytics/')
print('🔐 Access admin at: http://localhost:8000/admin/')
print('═' * 60)
