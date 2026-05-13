from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from courses.models import Announcement, Course, CourseMaterial, Lesson, LiveSession, QuizQuestion


COURSES = [
    {
        "title": "Python Foundations",
        "slug": "python-foundations",
        "category": "Backend",
        "level": "Beginner",
        "duration": "4 weeks",
        "price": 0,
        "summary": "Build clean Python basics through mini projects, quizzes, and guided practice.",
        "description": "Start with variables, control flow, functions, and data structures, then use those ideas in small programs that prepare you for Django.",
        "lessons": [
            ("Python syntax and variables", 35, "Write your first scripts and understand how Python stores values."),
            ("Functions and modules", 42, "Organize code into reusable functions and import modules."),
            ("Mini project", 55, "Build a command-line study planner with lists and dictionaries."),
        ],
        "materials": [
            ("Python starter notes", "https://docs.python.org/3/tutorial/", "Reading"),
            ("Practice exercises", "https://www.python.org/about/gettingstarted/", "Practice"),
        ],
        "announcements": [
            ("Welcome to Python Foundations", "Install Python and keep a notebook ready before the first Zoom class."),
        ],
        "quiz": [
            ("Which keyword defines a function in Python?", "func", "def", "make", "lambda", "B"),
            ("Which data type stores key-value pairs?", "List", "Tuple", "Dictionary", "String", "C"),
            ("What does import do?", "Deletes a module", "Loads a module", "Runs migrations", "Creates a class", "B"),
        ],
        "sessions": [
            ("Python setup clinic", 2, "https://zoom.us/j/12345678901", "123 4567 8901", "python101"),
            ("Functions live lab", 7, "https://zoom.us/j/12345678902", "123 4567 8902", "funcs"),
        ],
    },
    {
        "title": "Django Web Apps",
        "slug": "django-web-apps",
        "category": "Backend",
        "level": "Intermediate",
        "duration": "6 weeks",
        "price": 49,
        "summary": "Create database-backed Django apps with views, templates, URLs, and admin tools.",
        "description": "Learn the Django request cycle, create models, render templates, and use the admin to manage real course content.",
        "lessons": [
            ("Project setup", 30, "Create a Django project and app with clean settings."),
            ("Models and migrations", 50, "Design database tables and apply schema changes safely."),
            ("Views and templates", 45, "Connect URLs to Python views and render dynamic HTML."),
        ],
        "materials": [
            ("Django official tutorial", "https://docs.djangoproject.com/en/5.2/intro/tutorial01/", "Reading"),
            ("Project checklist", "https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/", "Checklist"),
        ],
        "announcements": [
            ("Django setup reminder", "Create your virtual environment before the live walkthrough."),
        ],
        "quiz": [
            ("Which file usually maps URL paths to views?", "urls.py", "models.py", "admin.py", "wsgi.py", "A"),
            ("What command applies database changes?", "python manage.py test", "python manage.py migrate", "python manage.py shell", "python manage.py collectstatic", "B"),
            ("What does a Django view return?", "A CSS file", "An HTTP response", "A database engine", "A migration number", "B"),
        ],
        "sessions": [
            ("Django project walkthrough", 3, "https://zoom.us/j/12345678903", "123 4567 8903", "django"),
            ("Models and migrations workshop", 9, "https://zoom.us/j/12345678904", "123 4567 8904", "models"),
        ],
    },
    {
        "title": "Frontend Essentials",
        "slug": "frontend-essentials",
        "category": "Frontend",
        "level": "Beginner",
        "duration": "3 weeks",
        "price": 29,
        "summary": "Learn HTML structure, modern CSS layouts, and JavaScript interactions.",
        "description": "Build accessible page structure, responsive layouts, and small JavaScript behaviors that make interfaces feel complete.",
        "lessons": [
            ("HTML page structure", 28, "Use semantic elements to organize content clearly."),
            ("CSS layout systems", 46, "Create responsive layouts with grid and flexbox."),
            ("JavaScript filtering", 38, "Add search and filter behavior to a course catalog."),
        ],
        "materials": [
            ("HTML reference", "https://developer.mozilla.org/en-US/docs/Web/HTML", "Reading"),
            ("CSS grid guide", "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout", "Reading"),
        ],
        "announcements": [
            ("Frontend studio prep", "Bring one page idea you want to turn into a responsive layout."),
        ],
        "quiz": [
            ("Which tag is best for page navigation?", "nav", "span", "b", "script", "A"),
            ("Which CSS feature creates two-dimensional layouts?", "Flexbox", "Grid", "Float", "Inline", "B"),
            ("Which event runs when a search field changes?", "input", "submit", "resize", "load", "A"),
        ],
        "sessions": [
            ("Responsive layout studio", 4, "https://zoom.us/j/12345678905", "123 4567 8905", "layout"),
            ("JavaScript Q&A", 10, "https://zoom.us/j/12345678906", "123 4567 8906", "js"),
        ],
    },
    {
        "title": "Full Stack Capstone",
        "slug": "full-stack-capstone",
        "category": "Full Stack",
        "level": "Advanced",
        "duration": "8 weeks",
        "price": 99,
        "summary": "Ship a polished learning dashboard that connects frontend behavior to Django data.",
        "description": "Combine Django models, forms, templates, and frontend polish to create a portfolio-ready LMS experience.",
        "lessons": [
            ("Data model planning", 35, "Map learners, courses, lessons, and enrollments."),
            ("Enrollment workflow", 48, "Build a secure form flow with validation and feedback."),
            ("Launch checklist", 32, "Review configuration, admin content, and next production steps."),
        ],
        "materials": [
            ("Capstone scope template", "https://docs.djangoproject.com/en/5.2/topics/testing/", "Template"),
            ("Launch checklist", "https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/", "Checklist"),
        ],
        "announcements": [
            ("Capstone kickoff", "Pick a project idea before the planning room opens."),
        ],
        "quiz": [
            ("Which layer stores course and quiz records?", "Template", "Model", "Static file", "Middleware", "B"),
            ("Which token protects POST forms in Django?", "CSRF token", "API token", "Style token", "Slug token", "A"),
            ("What should a launch checklist include?", "Only colors", "Only logo files", "Configuration and content review", "Only screenshots", "C"),
        ],
        "sessions": [
            ("Capstone planning room", 5, "https://zoom.us/j/12345678907", "123 4567 8907", "ship"),
            ("Launch review", 12, "https://zoom.us/j/12345678908", "123 4567 8908", "review"),
        ],
    },
]


class Command(BaseCommand):
    help = "Create sample Learnify courses and lessons."

    def handle(self, *args, **options):
        for course_data in COURSES:
            lessons = course_data["lessons"]
            materials = course_data["materials"]
            announcements = course_data["announcements"]
            quiz = course_data["quiz"]
            sessions = course_data["sessions"]
            defaults = {
                key: value
                for key, value in course_data.items()
                if key not in ["announcements", "lessons", "materials", "quiz", "sessions"]
            }
            course, _ = Course.objects.update_or_create(
                slug=course_data["slug"],
                defaults=defaults,
            )
            for index, (title, minutes, content) in enumerate(lessons, start=1):
                Lesson.objects.update_or_create(
                    course=course,
                    order=index,
                    defaults={
                        "title": title,
                        "duration_minutes": minutes,
                        "content": content,
                    },
                )
            for index, (title, material_url, material_type) in enumerate(materials, start=1):
                CourseMaterial.objects.update_or_create(
                    course=course,
                    order=index,
                    defaults={
                        "title": title,
                        "material_url": material_url,
                        "material_type": material_type,
                    },
                )
            for title, message in announcements:
                Announcement.objects.update_or_create(
                    course=course,
                    title=title,
                    defaults={"message": message},
                )
            for index, (question, option_a, option_b, option_c, option_d, correct_answer) in enumerate(quiz, start=1):
                QuizQuestion.objects.update_or_create(
                    course=course,
                    order=index,
                    defaults={
                        "question": question,
                        "option_a": option_a,
                        "option_b": option_b,
                        "option_c": option_c,
                        "option_d": option_d,
                        "correct_answer": correct_answer,
                    },
                )
            for index, (title, days_from_now, zoom_url, meeting_id, passcode) in enumerate(sessions, start=1):
                LiveSession.objects.update_or_create(
                    course=course,
                    title=title,
                    defaults={
                        "starts_at": timezone.now() + timedelta(days=days_from_now, hours=index),
                        "duration_minutes": 60,
                        "zoom_url": zoom_url,
                        "meeting_id": meeting_id,
                        "passcode": passcode,
                        "host_name": "Learnify mentor",
                    },
                )

        self.stdout.write(self.style.SUCCESS("Sample LMS content is ready."))
