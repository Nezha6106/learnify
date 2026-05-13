from django.core.management.base import BaseCommand
from django.db import transaction
from courses.models import Course, QuizQuestion


class Command(BaseCommand):
    help = 'Populate quiz banks with high-quality questions for all courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing quiz questions before populating',
        )

    def handle(self, *args, **options):
        # Define course-specific quiz content
        quiz_content = {
            'Django Web Apps': self.get_django_quiz_questions(),
            'Frontend Essentials': self.get_frontend_quiz_questions(),
            'Full Stack Capstone': self.get_fullstack_quiz_questions(),
            'Python Foundations': self.get_python_quiz_questions(),
        }

        if options['clear']:
            self.stdout.write('Clearing existing quiz questions...')
            QuizQuestion.objects.all().delete()
            self.stdout.write('All existing quiz questions cleared.')

        total_questions_created = 0
        courses_updated = 0

        with transaction.atomic():
            for course_title, questions in quiz_content.items():
                try:
                    course = Course.objects.get(title=course_title)
                    self.stdout.write(f'Processing course: {course_title}')
                    
                    # Clear existing questions for this course if not clearing all
                    if not options['clear']:
                        QuizQuestion.objects.filter(course=course).delete()
                    
                    course_questions_created = 0
                    for i, question_data in enumerate(questions, 1):
                        QuizQuestion.objects.create(
                            course=course,
                            question=question_data['question'],
                            option_a=question_data['options']['A'],
                            option_b=question_data['options']['B'],
                            option_c=question_data['options']['C'],
                            option_d=question_data['options']['D'],
                            correct_answer=question_data['correct_answer'],
                            order=i
                        )
                        course_questions_created += 1
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Created {course_questions_created} questions for {course_title}'
                    ))
                    total_questions_created += course_questions_created
                    courses_updated += 1

                except Course.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Course "{course_title}" not found in database. Skipping...'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Quiz population complete!\n'
            f'   • Courses updated: {courses_updated}\n'
            f'   • Total questions created: {total_questions_created}\n'
            f'   • Average questions per course: {total_questions_created / courses_updated if courses_updated > 0 else 0:.1f}'
        ))

    def get_django_quiz_questions(self):
        """Generate 20 Django-specific questions with progressive difficulty"""
        return [
            # Beginner Questions (1-7)
            {
                'question': 'What is the purpose of Django settings.py file?',
                'options': {
                    'A': 'To define database models',
                    'B': 'To configure Django project settings',
                    'C': 'To create HTML templates',
                    'D': 'To define URL patterns'
                },
                'correct_answer': 'B',
                'explanation': 'settings.py is the central configuration file where all Django project settings, database connections, and application configurations are defined.'
            },
            {
                'question': 'Which Django command creates a new app?',
                'options': {
                    'A': 'django-admin startapp',
                    'B': 'django-admin createapp',
                    'C': 'django-admin newapp',
                    'D': 'django-admin generateapp'
                },
                'correct_answer': 'A',
                'explanation': 'The "django-admin startapp" command creates a new Django application with the standard directory structure.'
            },
            {
                'question': 'What is the purpose of Django models.py?',
                'options': {
                    'A': 'To define HTML templates',
                    'B': 'To configure project settings',
                    'C': 'To define database structure and business logic',
                    'D': 'To create URL patterns'
                },
                'correct_answer': 'C',
                'explanation': 'models.py defines the database structure, fields, relationships, and business logic of your Django application.'
            },
            {
                'question': 'Which method is used to render HTML templates in Django views?',
                'options': {
                    'A': 'render_template()',
                    'B': 'html_response()',
                    'C': 'template_response()',
                    'D': 'render()'
                },
                'correct_answer': 'D',
                'explanation': 'The render() function combines a template with a context dictionary and returns an HttpResponse.'
            },
            {
                'question': 'What is Django ORM?',
                'options': {
                    'A': 'Object-Relational Mapping for HTML',
                    'B': 'Object-Relational Mapping for CSS',
                    'C': 'Object-Relational Mapping for databases',
                    'D': 'Object-Relational Mapping for JavaScript'
                },
                'correct_answer': 'C',
                'explanation': 'Django ORM is a powerful abstraction layer that allows you to perform database operations using Python objects instead of raw SQL.'
            },
            {
                'question': 'Which Django template tag is used for URL routing?',
                'options': {
                    'A': '{% url %}',
                    'B': '{% path %}',
                    'C': '{% route %}',
                    'D': '{% link %}'
                },
                'correct_answer': 'A',
                'explanation': 'The {% url %} template tag generates URLs based on the URL configuration defined in urls.py.'
            },
            # Intermediate Questions (8-14)
            {
                'question': 'What is the purpose of Django migrations?',
                'options': {
                    'A': 'To backup the database',
                    'B': 'To track changes in models and synchronize the database schema',
                    'C': 'To optimize query performance',
                    'D': 'To create HTML templates'
                },
                'correct_answer': 'B',
                'explanation': 'Migrations track model changes and allow the database schema to be versioned and applied consistently across different environments.'
            },
            {
                'question': 'What is Django middleware?',
                'options': {
                    'A': 'Software that connects Django to databases',
                    'B': 'A hook that processes requests globally before/after view execution',
                    'C': 'A template engine for rendering HTML',
                    'D': 'A security system for user authentication'
                },
                'correct_answer': 'B',
                'explanation': 'Middleware is a framework of hooks that process requests and responses globally, enabling cross-cutting concerns like authentication, logging, and security.'
            },
            {
                'question': 'Which Django field type is best for storing JSON data?',
                'options': {
                    'A': 'CharField',
                    'B': 'TextField',
                    'C': 'JSONField',
                    'D': 'BinaryField'
                },
                'correct_answer': 'C',
                'explanation': 'JSONField is specifically designed to store JSON data efficiently and provides JSON-specific operations and validation.'
            },
            {
                'question': 'What is the purpose of the Django admin site?',
                'options': {
                    'A': 'To create HTML templates',
                    'B': 'To provide a built-in management interface for data models',
                    'C': 'To configure project settings',
                    'D': 'To handle user authentication'
                },
                'correct_answer': 'B',
                'explanation': 'Django admin automatically generates a professional interface for managing application data models with minimal code.'
            },
            {
                'question': 'What is the Django request-response cycle?',
                'options': {
                    'A': 'Request → View → Template → Response',
                    'B': 'Template → View → Request → Response',
                    'C': 'Response → Template → View → Request',
                    'D': 'View → Request → Template → Response'
                },
                'correct_answer': 'A',
                'explanation': 'Django follows the MVT (Model-View-Template) pattern where HTTP requests are processed by views, which use templates to generate responses.'
            },
            # Advanced Questions (15-20)
            {
                'question': 'What is Django QuerySet optimization?',
                'options': {
                    'A': 'Using select_related() and prefetch_related()',
                    'B': 'Adding more indexes to the database',
                    'C': 'Using raw SQL queries',
                    'D': 'Caching all responses'
                },
                'correct_answer': 'A',
                'explanation': 'select_related() and prefetch_related() optimize database queries by reducing the number of database hits through efficient SQL joins.'
            },
            {
                'question': 'What are Django signals?',
                'options': {
                    'A': 'A way to send emails',
                    'B': 'A system that allows decoupled applications to get notified when certain actions occur',
                    'C': 'A security feature for authentication',
                    'D': 'A template rendering optimization'
                },
                'correct_answer': 'B',
                'explanation': 'Signals allow applications to respond to Django framework events, enabling loose coupling and event-driven architecture.'
            },
            {
                'question': 'What is the purpose of Django context processors?',
                'options': {
                    'A': 'To process HTML templates',
                    'B': 'To add variables to all templates globally',
                    'C': 'To handle database connections',
                    'D': 'To configure URL routing'
                },
                'correct_answer': 'B',
                'explanation': 'Context processors add variables to the template context, making data available across all templates without explicit passing.'
            },
            {
                'question': 'What is the Django REST framework?',
                'options': {
                    'A': 'A library for creating RESTful APIs with Django',
                    'B': 'A template engine for REST APIs',
                    'C': 'A database optimization tool',
                    'D': 'A security enhancement for Django'
                },
                'correct_answer': 'A',
                'explanation': 'Django REST Framework provides powerful tools for building RESTful APIs, including serializers, viewsets, and routers.'
            },
            {
                'question': 'What is Django template inheritance?',
                'options': {
                    'A': 'Creating multiple template files and combining them',
                    'B': 'Using {% extends %} to inherit from base templates',
                    'C': 'Using {% include %} to reuse template sections',
                    'D': 'All of the above'
                },
                'correct_answer': 'D',
                'explanation': 'Django template inheritance uses {% extends %} for base templates and {% include %} for reusable components, promoting DRY principles.'
            },
            {
                'question': 'What is the Django cache framework?',
                'options': {
                    'A': 'A way to store frequently accessed data in memory',
                    'B': 'A database backup system',
                    'C': 'A template optimization technique',
                    'D': 'A security feature'
                },
                'correct_answer': 'A',
                'explanation': 'Django cache framework provides multiple backends (memory, file, database, Redis) to store frequently accessed data and improve performance.'
            }
        ]

    def get_frontend_quiz_questions(self):
        """Generate 20 Frontend-specific questions with progressive difficulty"""
        return [
            # Beginner Questions (1-7)
            {
                'question': 'What is the purpose of the CSS Box Model?',
                'options': {
                    'A': 'To create 3D layouts',
                    'B': 'To define how HTML elements are rendered as rectangular boxes',
                    'C': 'To style text content',
                    'D': 'To create responsive designs'
                },
                'correct_answer': 'B',
                'explanation': 'The CSS Box Model describes how every HTML element is rendered as a rectangular box with content, padding, border, and margin.'
            },
            {
                'question': 'Which CSS property is used to create flexible layouts?',
                'options': {
                    'A': 'display: grid',
                    'B': 'display: flex',
                    'C': 'display: block',
                    'D': 'position: relative'
                },
                'correct_answer': 'B',
                'explanation': 'Flexbox provides a powerful way to create flexible, responsive layouts with efficient alignment and distribution of space.'
            },
            {
                'question': 'What is the difference between inline and block elements?',
                'options': {
                    'A': 'Inline elements have margins, block elements have padding',
                    'B': 'Block elements take full width, inline elements take only necessary width',
                    'C': 'Inline elements cannot contain block elements, block elements can contain inline',
                    'D': 'There is no difference in modern CSS'
                },
                'correct_answer': 'C',
                'explanation': 'Block elements create line breaks and take full available width, while inline elements flow with content and cannot contain block elements.'
            },
            {
                'question': 'What is responsive web design?',
                'options': {
                    'A': 'Design that looks the same on all devices',
                    'B': 'Design that adapts to different screen sizes and devices',
                    'C': 'Design that only works on mobile devices',
                    'D': 'Design that uses only CSS media queries'
                },
                'correct_answer': 'B',
                'explanation': 'Responsive web design ensures websites adapt and display optimally across various devices, screen sizes, and orientations.'
            },
            {
                'question': 'What is the purpose of CSS Grid?',
                'options': {
                    'A': 'To create flexible one-dimensional layouts',
                    'B': 'To create two-dimensional layouts with rows and columns',
                    'C': 'To style text content',
                    'D': 'To create 3D transformations'
                },
                'correct_answer': 'B',
                'explanation': 'CSS Grid is a two-dimensional layout system that enables complex responsive designs with precise control over rows and columns.'
            },
            {
                'question': 'What is the CSS "cascading" principle?',
                'options': {
                    'A': 'Styles flow from parent to child elements',
                    'B': 'More specific selectors override less specific ones',
                    'C': 'Styles are applied in order of specificity and source order',
                    'D': 'All of the above'
                },
                'correct_answer': 'D',
                'explanation': 'CSS cascading means styles flow down, are inherited, and can be overridden based on specificity and source order.'
            },
            {
                'question': 'What is the purpose of CSS media queries?',
                'options': {
                    'A': 'To query databases',
                    'B': 'To apply different styles based on device characteristics',
                    'C': 'To optimize images',
                    'D': 'To create animations'
                },
                'correct_answer': 'B',
                'explanation': 'Media queries enable responsive design by applying different CSS styles based on device characteristics like screen size, resolution, and orientation.'
            },
            # Intermediate Questions (8-14)
            {
                'question': 'What is CSS specificity?',
                'options': {
                    'A': 'The order in which CSS rules are applied',
                    'B': 'A way to make CSS more important',
                    'C': 'A method for organizing CSS files',
                    'D': 'A technique for debugging CSS'
                },
                'correct_answer': 'A',
                'explanation': 'CSS specificity determines which rules apply when multiple rules target the same element, based on selector specificity and source order.'
            },
            {
                'question': 'What is the difference between relative and absolute positioning?',
                'options': {
                    'A': 'Relative is positioned relative to parent, absolute is fixed to viewport',
                    'B': 'Relative maintains document flow, absolute removes from flow',
                    'C': 'Relative uses top/left, absolute uses transform',
                    'D': 'There is no difference in modern browsers'
                },
                'correct_answer': 'B',
                'explanation': 'Relative positioning maintains element in document flow, while absolute positioning removes elements from normal flow and positions them relative to containing blocks.'
            },
            {
                'question': 'What are CSS custom properties (variables)?',
                'options': {
                    'A': 'Properties that can be changed by users',
                    'B': 'Browser-specific CSS properties',
                    'C': 'Properties for creating animations',
                    'D': 'Properties that must be prefixed'
                },
                'correct_answer': 'A',
                'explanation': 'CSS custom properties allow defining reusable values that can be referenced throughout a stylesheet, enabling dynamic theming and consistent design.'
            },
            {
                'question': 'What is the CSS "rem" unit?',
                'options': {
                    'A': 'Relative to the root element font size',
                    'B': 'Relative to the parent element font size',
                    'C': 'A fixed pixel value',
                    'D': 'A percentage of the viewport width'
                },
                'correct_answer': 'A',
                'explanation': 'The "rem" unit is relative to the root element (html) font size, making it ideal for accessible, scalable typography.'
            },
            {
                'question': 'What is CSS Grid\'s "fr" unit?',
                'options': {
                    'A': 'A fixed fraction unit',
                    'B': 'A flexible length unit representing a fraction of available space in the grid container',
                    'C': 'A font-related unit',
                    'D': 'A pixel-based unit'
                },
                'correct_answer': 'B',
                'explanation': 'The "fr" unit represents a fraction of available grid space, enabling flexible, responsive grid layouts without calculations.'
            },
            {
                'question': 'What is the CSS "will-change" property?',
                'options': {
                    'A': 'To create animations',
                    'B': 'To optimize browser rendering performance',
                    'C': 'To tell browser which properties will change',
                    'D': 'To handle browser compatibility'
                },
                'correct_answer': 'B',
                'explanation': 'The "will-change" property hints to browsers about upcoming changes, allowing them to optimize rendering by preparing only the necessary resources.'
            },
            # Advanced Questions (15-20)
            {
                'question': 'What is CSS containment?',
                'options': {
                    'A': 'A way to isolate parts of a page from the rest',
                    'B': 'A security feature for CSS',
                    'C': 'A method for organizing CSS code',
                    'D': 'A technique for creating animations'
                },
                'correct_answer': 'A',
                'explanation': 'CSS containment isolates portions of the DOM, allowing browsers to optimize rendering independently and improve performance.'
            },
            {
                'question': 'What is the CSS "content-visibility" property?',
                'options': {
                    'A': 'To control element visibility',
                    'B': 'To optimize rendering of off-screen content',
                    'C': 'To create lazy loading effects',
                    'D': 'To handle browser compatibility'
                },
                'correct_answer': 'B',
                'explanation': 'The "content-visibility" property allows developers to control whether content is rendered and whether its state is maintained in memory, optimizing performance.'
            },
            {
                'question': 'What are CSS logical properties?',
                'options': {
                    'A': 'Properties that follow mathematical logic',
                    'B': 'Properties for right-to-left languages',
                    'C': 'Properties that adapt to writing direction and document structure',
                    'D': 'Properties for debugging CSS'
                },
                'correct_answer': 'C',
                'explanation': 'CSS logical properties like "margin-inline-start" adapt to writing direction and document structure, making styles more maintainable for international audiences.'
            },
            {
                'question': 'What is the CSS "inset" property?',
                'options': {
                    'A': 'A shorthand for top, right, bottom, and left positioning',
                    'B': 'A way to create shadows',
                    'C': 'A method for centering elements',
                    'D': 'A grid layout technique'
                },
                'correct_answer': 'A',
                'explanation': 'The "inset" property is a shorthand that sets top, right, bottom, and left properties simultaneously, useful for positioning and shadows.'
            },
            {
                'question': 'What is the CSS "gap" property in Grid and Flexbox?',
                'options': {
                    'A': 'The space between grid lines or flex items',
                    'B': 'A way to create margins',
                    'C': 'A padding technique',
                    'D': 'A border styling method'
                },
                'correct_answer': 'A',
                'explanation': 'The "gap" property provides a concise way to create consistent spacing between grid tracks or flex items, improving layout maintainability.'
            },
            {
                'question': 'What is the CSS "container" query?',
                'options': {
                    'A': 'A way to style containers',
                    'B': 'A media query for container-based layouts',
                    'C': 'A method for responsive design',
                    'D': 'A security feature'
                },
                'correct_answer': 'B',
                'explanation': 'Container queries enable responsive design based on the size of a container element rather than the viewport, providing more component-based responsive design.'
            }
        ]

    def get_fullstack_quiz_questions(self):
        """Generate 20 Full Stack Capstone questions with progressive difficulty"""
        return [
            # Beginner Questions (1-7)
            {
                'question': 'What is the primary purpose of version control systems like Git?',
                'options': {
                    'A': 'To deploy applications',
                    'B': 'To track changes in code over time and enable collaboration',
                    'C': 'To optimize database performance',
                    'D': 'To create backup systems'
                },
                'correct_answer': 'B',
                'explanation': 'Version control systems like Git track code changes, enable collaboration, and provide mechanisms for reverting changes and managing releases.'
            },
            {
                'question': 'Which HTTP method is typically used for creating new resources?',
                'options': {
                    'A': 'GET',
                    'B': 'POST',
                    'C': 'PUT',
                    'D': 'DELETE'
                },
                'correct_answer': 'B',
                'explanation': 'POST is the standard HTTP method for creating new resources, as it sends data in the request body rather than URL parameters.'
            },
            {
                'question': 'What is the purpose of REST APIs?',
                'options': {
                    'A': 'To create user interfaces',
                    'B': 'To provide a standardized architectural style for web services',
                    'C': 'To optimize database queries',
                    'D': 'To secure web applications'
                },
                'correct_answer': 'B',
                'explanation': 'REST (Representational State Transfer) provides a standardized architectural style using HTTP methods, stateless communication, and resource-based URLs.'
            },
            {
                'question': 'What is the difference between authentication and authorization?',
                'options': {
                    'A': 'Authentication is who you are, authorization is what you can do',
                    'B': 'Authentication verifies identity, authorization grants permissions',
                    'C': 'Authentication is for servers, authorization is for clients',
                    'D': 'They are the same thing'
                },
                'correct_answer': 'B',
                'explanation': 'Authentication verifies who a user is, while authorization determines what permissions and resources that authenticated user can access.'
            },
            {
                'question': 'What is the purpose of environment variables?',
                'options': {
                    'A': 'To store application configuration',
                    'B': 'To optimize code performance',
                    'C': 'To create global variables',
                    'D': 'To handle database connections'
                },
                'correct_answer': 'A',
                'explanation': 'Environment variables store configuration settings like database credentials, API keys, and deployment-specific parameters outside of code.'
            },
            {
                'question': 'What is the purpose of API documentation?',
                'options': {
                    'A': 'To optimize code for search engines',
                    'B': 'To provide developers with instructions for using an API',
                    'C': 'To create user interfaces',
                    'D': 'To test API functionality'
                },
                'correct_answer': 'B',
                'explanation': 'API documentation provides developers with essential information about endpoints, parameters, authentication, and usage examples for effective integration.'
            },
            # Intermediate Questions (8-14)
            {
                'question': 'What is the purpose of a package.json file?',
                'options': {
                    'A': 'To configure database settings',
                    'B': 'To define project metadata and dependencies',
                    'C': 'To create HTML templates',
                    'D': 'To handle user authentication'
                },
                'correct_answer': 'B',
                'explanation': 'package.json defines project metadata, dependencies, scripts, and configuration for modern web development tools and package managers.'
            },
            {
                'question': 'What is the difference between SQL and NoSQL databases?',
                'options': {
                    'A': 'SQL is for structured data, NoSQL is for unstructured',
                    'B': 'SQL uses tables, NoSQL uses documents',
                    'C': 'SQL is relational, NoSQL is non-relational',
                    'D': 'All of the above'
                },
                'correct_answer': 'D',
                'explanation': 'SQL databases use structured schemas with tables and relationships, while NoSQL databases offer flexible schemas for various data models and use cases.'
            },
            {
                'question': 'What is the purpose of a build tool like Webpack?',
                'options': {
                    'A': 'To write documentation',
                    'B': 'To bundle and optimize web assets for production',
                    'C': 'To create database migrations',
                    'D': 'To deploy applications'
                },
                'correct_answer': 'B',
                'explanation': 'Build tools like Webpack bundle JavaScript, CSS, and other assets, optimize them for production, and handle dependencies and transformations.'
            },
            {
                'question': 'What is the difference between PUT and PATCH?',
                'options': {
                    'A': 'PUT replaces entire resource, PATCH modifies partially',
                    'B': 'PUT creates new resources, PATCH updates existing',
                    'C': 'PUT is for clients, PATCH is for servers',
                    'D': 'They are identical'
                },
                'correct_answer': 'A',
                'explanation': 'PUT replaces the entire resource with a new representation, while PATCH applies partial modifications to existing resources.'
            },
            {
                'question': 'What is the purpose of a reverse proxy?',
                'options': {
                    'A': 'To cache static files',
                    'B': 'To forward client requests to backend servers and route responses',
                    'C': 'To encrypt communications',
                    'D': 'To balance load across servers'
                },
                'correct_answer': 'B',
                'explanation': 'A reverse proxy forwards client requests to appropriate backend servers, providing load balancing, SSL termination, and URL routing.'
            },
            {
                'question': 'What is the purpose of CI/CD pipelines?',
                'options': {
                    'A': 'To automatically deploy applications',
                    'B': 'To automate testing, building, and deployment processes',
                    'C': 'To monitor application performance',
                    'D': 'To manage database backups'
                },
                'correct_answer': 'B',
                'explanation': 'CI/CD pipelines automate the software delivery process, ensuring consistent testing, building, and deployment of applications to production environments.'
            },
            # Advanced Questions (15-20)
            {
                'question': 'What is the purpose of a Content Delivery Network (CDN)?',
                'options': {
                    'A': 'To store application code',
                    'B': 'To distribute content globally and improve performance',
                    'C': 'To secure web applications',
                    'D': 'To manage database connections'
                },
                'correct_answer': 'B',
                'explanation': 'CDNs distribute content across geographically distributed servers, reducing latency and improving performance for global users.'
            },
            {
                'question': 'What is the difference between monolithic and microservices architecture?',
                'options': {
                    'A': 'Monolithic is faster, microservices are more scalable',
                    'B': 'Monolithic is single unit, microservices are distributed services',
                    'C': 'Monolithic is for small apps, microservices for large apps',
                    'D': 'They are identical in modern development'
                },
                'correct_answer': 'B',
                'explanation': 'Monolithic applications are built as single units, while microservices break applications into small, independent services that communicate via APIs.'
            },
            {
                'question': 'What is the purpose of containerization?',
                'options': {
                    'A': 'To secure applications',
                    'B': 'To package applications with dependencies for consistent deployment',
                    'C': 'To optimize performance',
                    'D': 'To create virtual machines'
                },
                'correct_answer': 'B',
                'explanation': 'Containerization packages applications with their dependencies into isolated environments, ensuring consistent deployment across different platforms.'
            },
            {
                'question': 'What is the purpose of load balancing?',
                'options': {
                    'A': 'To distribute network traffic across multiple servers',
                    'B': 'To optimize database queries',
                    'C': 'To cache static content',
                    'D': 'To compress response data'
                },
                'correct_answer': 'A',
                'explanation': 'Load balancing distributes incoming network traffic across multiple servers to improve performance, reliability, and availability of web applications.'
            },
            {
                'question': 'What is the purpose of monitoring and observability?',
                'options': {
                    'A': 'To fix bugs in production',
                    'B': 'To gain insights into system performance and user behavior',
                    'C': 'To optimize database performance',
                    'D': 'To automate deployment processes'
                },
                'correct_answer': 'B',
                'explanation': 'Monitoring and observability provide visibility into system health, performance metrics, and user behavior to enable proactive issue resolution and optimization.'
            },
            {
                'question': 'What is the difference between synchronous and asynchronous programming?',
                'options': {
                    'A': 'Synchronous executes sequentially, asynchronous executes concurrently',
                    'B': 'Synchronous is faster, asynchronous is more complex',
                    'C': 'Synchronous is for single-threaded, asynchronous is for multi-threaded',
                    'D': 'They are identical in modern JavaScript'
                },
                'correct_answer': 'A',
                'explanation': 'Synchronous code executes sequentially and blocks until completion, while asynchronous code can handle multiple operations concurrently without blocking.'
            }
        ]

    def get_python_quiz_questions(self):
        """Generate 20 Python questions with progressive difficulty"""
        return [
            # Beginner Questions (1-7)
            {
                'question': 'What is the correct way to create a variable in Python?',
                'options': {
                    'A': 'var x = 5',
                    'B': 'x = 5',
                    'C': 'variable x = 5',
                    'D': 'declare x = 5'
                },
                'correct_answer': 'B',
                'explanation': 'In Python, variables are created by simple assignment: variable_name = value. No keywords like "var" or "declare" are needed.'
            },
            {
                'question': 'Which of the following is a valid Python data type?',
                'options': {
                    'A': 'integer',
                    'B': 'string',
                    'C': 'boolean',
                    'D': 'All of the above'
                },
                'correct_answer': 'D',
                'explanation': 'Python supports multiple built-in data types including integers, strings, and booleans.'
            },
            {
                'question': 'How do you start a comment in Python?',
                'options': {
                    'A': '// This is a comment',
                    'B': '# This is a comment',
                    'C': '/* This is a comment */',
                    'D': '-- This is a comment'
                },
                'correct_answer': 'B',
                'explanation': 'Python uses the hash symbol (#) to start single-line comments.'
            },
            {
                'question': 'What is the output of: print(len("Hello World"))?',
                'options': {
                    'A': 'Hello World',
                    'B': '11',
                    'C': '5',
                    'D': 'Error'
                },
                'correct_answer': 'B',
                'explanation': 'The len() function returns the number of characters in the string "Hello World", which is 11.'
            },
            {
                'question': 'Which method is used to add an element to a list in Python?',
                'options': {
                    'A': 'append()',
                    'B': 'add()',
                    'C': 'insert()',
                    'D': 'push()'
                },
                'correct_answer': 'A',
                'explanation': 'The append() method adds an element to the end of a list in Python.'
            },
            {
                'question': 'What is the correct file extension for Python files?',
                'options': {
                    'A': '.py',
                    'B': '.python',
                    'C': '.pt',
                    'D': '.pyth'
                },
                'correct_answer': 'A',
                'explanation': 'Python files use the .py extension by convention.'
            },
            {
                'question': 'Which keyword is used to define a function in Python?',
                'options': {
                    'A': 'function',
                    'B': 'def',
                    'C': 'func',
                    'D': 'define'
                },
                'correct_answer': 'B',
                'explanation': 'The "def" keyword is used to define functions in Python.'
            },
            # Intermediate Questions (8-14)
            {
                'question': 'What is list comprehension in Python?',
                'options': {
                    'A': 'A way to create lists using loops and conditions',
                    'B': 'A method to sort lists',
                    'C': 'A way to merge two lists',
                    'D': 'A built-in function for list operations'
                },
                'correct_answer': 'A',
                'explanation': 'List comprehension is a concise way to create lists using loops and conditional logic in a single line.'
            },
            {
                'question': 'What does the "self" parameter represent in Python classes?',
                'options': {
                    'A': 'The class name',
                    'B': 'The instance of the class',
                    'C': 'The parent class',
                    'D': 'The module name'
                },
                'correct_answer': 'B',
                'explanation': 'The "self" parameter represents the instance of the class and allows access to instance variables and methods.'
            },
            {
                'question': 'Which of the following is a mutable data type in Python?',
                'options': {
                    'A': 'tuple',
                    'B': 'string',
                    'C': 'list',
                    'D': 'integer'
                },
                'correct_answer': 'C',
                'explanation': 'Lists are mutable in Python, meaning they can be modified after creation. Tuples and strings are immutable.'
            },
            {
                'question': 'What is the purpose of the __init__ method in Python classes?',
                'options': {
                    'A': 'To delete an object',
                    'B': 'To initialize object attributes',
                    'C': 'To compare objects',
                    'D': 'To convert object to string'
                },
                'correct_answer': 'B',
                'explanation': 'The __init__ method is a constructor that initializes object attributes when an instance is created.'
            },
            {
                'question': 'How do you handle exceptions in Python?',
                'options': {
                    'A': 'try-except blocks',
                    'B': 'if-else statements',
                    'C': 'assert statements',
                    'D': 'logging statements'
                },
                'correct_answer': 'A',
                'explanation': 'Python uses try-except blocks to handle exceptions and prevent program crashes.'
            },
            {
                'question': 'What is a decorator in Python?',
                'options': {
                    'A': 'A way to modify function behavior',
                    'B': 'A type of loop',
                    'C': 'A method for organizing code',
                    'D': 'A security feature'
                },
                'correct_answer': 'A',
                'explanation': 'Decorators are functions that modify the behavior of other functions without changing their source code, often used for logging, timing, or validation.'
            },
            {
                'question': 'What is the difference between __str__ and __repr__ in Python?',
                'options': {
                    'A': '__str__ is for debugging, __repr__ is for users',
                    'B': '__str__ is for users, __repr__ is for debugging',
                    'C': 'They are identical',
                    'D': '__str__ is faster than __repr__'
                },
                'correct_answer': 'B',
                'explanation': '__str__ returns a user-friendly string representation, while __repr__ returns an unambiguous developer representation.'
            },
            # Advanced Questions (15-20)
            {
                'question': 'What is the Global Interpreter Lock (GIL) in Python?',
                'options': {
                    'A': 'A mechanism to prevent multiple threads from executing Python bytecode simultaneously',
                    'B': 'A security feature for code execution',
                    'C': 'A memory management system',
                    'D': 'A type checking mechanism'
                },
                'correct_answer': 'A',
                'explanation': 'The GIL ensures that only one thread executes Python bytecode at a time, affecting multi-threading performance.'
            },
            {
                'question': 'What is metaprogramming in Python?',
                'options': {
                    'A': 'Writing programs that write or manipulate other programs',
                    'B': 'Programming with metadata',
                    'C': 'A way to organize large codebases',
                    'D': 'A testing methodology'
                },
                'correct_answer': 'A',
                'explanation': 'Metaprogramming involves writing code that can manipulate, generate, or analyze other code, enabling dynamic code generation.'
            },
            {
                'question': 'What is the purpose of context managers (with statement) in Python?',
                'options': {
                    'A': 'To improve code performance',
                    'B': 'To automatically manage resources and cleanup',
                    'C': 'To create class hierarchies',
                    'D': 'To handle exceptions globally'
                },
                'correct_answer': 'B',
                'explanation': 'Context managers automatically handle setup and cleanup operations, ensuring resources are properly managed.'
            },
            {
                'question': 'What are Python descriptors?',
                'options': {
                    'A': 'Objects that manage attribute access',
                    'B': 'Type hints for variables',
                    'C': 'Documentation strings',
                    'D': 'Testing utilities'
                },
                'correct_answer': 'A',
                'explanation': 'Descriptors are objects that define how attribute access is managed through __get__, __set__, and __delete__ methods.'
            },
            {
                'question': 'What is the difference between shallow copy and deep copy in Python?',
                'options': {
                    'A': 'Shallow copy copies references, deep copy creates independent objects',
                    'B': 'Deep copy copies references, shallow copy creates independent objects',
                    'C': 'They are identical',
                    'D': 'Shallow copy is faster, deep copy is slower but same result'
                },
                'correct_answer': 'A',
                'explanation': 'Shallow copy duplicates object references, while deep copy recursively copies all objects, creating independent copies.'
            },
            {
                'question': 'What is asyncio in Python?',
                'options': {
                    'A': 'A library for synchronous programming',
                    'B': 'A library for asynchronous programming using coroutines',
                    'C': 'A database connection library',
                    'D': 'A web framework'
                },
                'correct_answer': 'B',
                'explanation': 'Asyncio provides infrastructure for writing single-threaded concurrent code using coroutines and event loops.'
            }
        ]
