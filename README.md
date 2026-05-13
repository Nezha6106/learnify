# Learnify - Django LMS With Zoom Meetings

Learnify is a complete learning management system project built with Django, Python, HTML, CSS, and JavaScript. It includes student login/signup, course enrollment, live Zoom classes, course materials, announcements, quizzes, marks, reports, and admin management.

## Features

- Student signup, login, logout, and protected dashboard
- Course catalog with search and category filters
- Course detail pages with lessons, announcements, materials, quizzes, and Zoom classes
- User-linked course enrollment
- Zoom meeting links with schedule, meeting ID, passcode, duration, and host name
- Course materials/resources that enrolled students can open
- Quiz submission with marks and percentage
- Student performance report by email
- Django admin for managing courses, lessons, materials, announcements, Zoom classes, quiz questions, enrollments, and attempts
- Seed command with sample courses and demo Zoom links
- Responsive frontend using plain HTML, CSS, and JavaScript

## Project Structure

```text
learnify/
  settings.py
  urls.py
courses/
  models.py
  views.py
  forms.py
  admin.py
  urls.py
  templates/
    courses/
      home.html
      detail.html
      dashboard.html
      report.html
    registration/
      login.html
      signup.html
  static/courses/
    styles.css
    app.js
  management/commands/
    seed_lms.py
```

## Main Pages

```text
/                         Course catalog and upcoming live classes
/signup/                  Create student account
/accounts/login/          Student/admin login
/dashboard/               Student dashboard
/courses/<course-slug>/   Lessons, materials, Zoom meetings, quiz, enrollment
/reports/                 Student marks and progress report
/admin/                   Admin panel
```

## Setup

Install Django if needed:

```powershell
pip install django
```

Apply database migrations:

```powershell
python manage.py migrate
```

Load sample LMS data:

```powershell
python manage.py seed_lms
```

Run the project:

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Admin

Create an admin user:

```powershell
python manage.py createsuperuser
```

Then open:

```text
http://127.0.0.1:8000/admin/
```

You can manage:

- Courses
- Lessons
- Course materials
- Announcements
- Zoom live sessions
- Quiz questions
- Enrollments
- Quiz attempts

## Zoom Meetings

This project stores Zoom meeting links and details in the `LiveSession` model. In the admin panel, open a course and add live sessions with:

- Title
- Start date and time
- Duration
- Zoom URL
- Meeting ID
- Passcode
- Host name

Students can see Zoom meeting details after enrolling in the course. Replace the sample `https://zoom.us/j/...` links with your real Zoom links.

## Testing

Run:

```powershell
python manage.py test
```

Current tests cover signup, dashboard login protection, enrollment, and Zoom access for enrolled students.
