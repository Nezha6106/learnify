from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.utils.decorators import method_decorator

from .forms import (
    CourseModelForm, EnrollmentForm, QuizSubmissionForm,
    ReportLookupForm, SignUpForm, UserProfileForm, CourseSearchForm
)
from django.contrib.auth.models import User

from .models import Course, Enrollment, LiveSession, QuizAttempt, UserProfile, QuizSession, StudentAnalytics


def admin_access(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin:index")

    if request.user.is_authenticated:
        messages.error(request, "Admin access is only available for staff accounts.")
        return redirect("home")

    messages.info(request, "Sign in with an admin account to open the admin panel.")
    return redirect(f"{reverse('login')}?next={reverse('admin_access')}")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            full_name = form.cleaned_data.get("full_name", "").strip()
            if full_name:
                first_name, _, last_name = full_name.partition(" ")
                user.first_name = first_name
                user.last_name = last_name
            if user.username.lower() == "admin":
                user.is_staff = True
                user.is_superuser = True
            user.save()
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data.get("role", "student"),
            )
            messages.success(request, "Account created. Sign in with your new username and password.")
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("user_profile")
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, "courses/user_profile.html", {"form": form, "profile": profile})


def home(request):
    search_form = CourseSearchForm(request.GET or None)
    courses = Course.objects.filter(is_published=True).prefetch_related("lessons", "live_sessions", "materials")
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        level = search_form.cleaned_data.get('level')
        price_min = search_form.cleaned_data.get('price_min')
        price_max = search_form.cleaned_data.get('price_max')
        
        if query:
            courses = courses.filter(
                models.Q(title__icontains=query) | 
                models.Q(summary__icontains=query) | 
                models.Q(description__icontains=query)
            )
        if category:
            courses = courses.filter(category__icontains=category)
        if level:
            courses = courses.filter(level=level)
        if price_min is not None:
            courses = courses.filter(price__gte=price_min)
        if price_max is not None:
            courses = courses.filter(price__lte=price_max)
    
    upcoming_sessions = LiveSession.objects.filter(course__is_published=True).select_related("course")[:3]
    stats = {
        "learners": Enrollment.objects.count(),
        "courses": courses.count(),
        "lessons": sum(course.lessons.count() for course in courses),
        "attempts": QuizAttempt.objects.count(),
        "sessions": LiveSession.objects.count(),
    }
    return render(
        request,
        "courses/home.html",
        {"courses": courses, "stats": stats, "upcoming_sessions": upcoming_sessions, "search_form": search_form},
    )


@login_required
def dashboard(request):
    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .select_related("course")
        .prefetch_related("course__lessons", "course__live_sessions", "course__materials", "course__announcements")
    )
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    attempts = QuizAttempt.objects.filter(user=request.user).select_related("course")[:8]
    sessions = LiveSession.objects.filter(course__in=enrolled_courses).select_related("course")[:8]
    return render(
        request,
        "courses/dashboard.html",
        {
            "enrollments": enrollments,
            "attempts": attempts,
            "sessions": sessions,
        },
    )


@login_required
def analytics_dashboard(request):
    """Display student analytics and learning progress"""
    analytics, created = StudentAnalytics.objects.get_or_create(user=request.user)
    
    # Get enrollment data
    enrollments = request.user.enrollments.select_related('course')
    enrolled_courses = [e.course for e in enrollments]
    
    # Get quiz performance data
    quiz_attempts = request.user.quiz_attempts.select_related('course').order_by('-submitted_at')[:10]
    
    # Calculate statistics
    total_quizzes = quiz_attempts.count()
    if total_quizzes > 0:
        avg_score = sum(q.percentage for q in quiz_attempts) / total_quizzes
        analytics.average_quiz_score = avg_score
        analytics.total_quiz_attempts = total_quizzes
        analytics.save(update_fields=['average_quiz_score', 'total_quiz_attempts'])
    
    # Prepare performance by course
    course_performance = []
    for course in enrolled_courses:
        attempts = quiz_attempts.filter(course=course)
        if attempts.exists():
            avg = sum(q.percentage for q in attempts) / attempts.count()
            course_performance.append({
                'course': course,
                'attempts': attempts.count(),
                'average_score': round(avg),
                'status': 'Completed' if attempts.exists() else 'In Progress',
            })
    
    context = {
        'analytics': analytics,
        'enrollments': enrollments,
        'quiz_attempts': quiz_attempts,
        'course_performance': course_performance,
        'total_enrolled': enrollments.count(),
        'total_quizzes': total_quizzes,
        'avg_quiz_score': round(analytics.average_quiz_score, 1),
    }
    return render(request, 'courses/analytics_dashboard.html', context)


def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related("announcements", "lessons", "materials", "quiz_questions", "live_sessions"),
        slug=slug,
        is_published=True,
    )
    questions = list(course.quiz_questions.all())
    enrollment_form = EnrollmentForm(user=request.user)
    quiz_form = QuizSubmissionForm(questions=questions)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(course=course, user=request.user).exists()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "enroll":
            if not request.user.is_authenticated:
                messages.info(request, "Create an account or sign in before joining a course.")
                return redirect(f"{reverse('login')}?next={course.get_absolute_url()}")

            enrollment_form = EnrollmentForm(request.POST, user=request.user)
            if enrollment_form.is_valid():
                enrollment = enrollment_form.save(commit=False)
                enrollment.course = course
                enrollment.user = request.user
                if not enrollment.email:
                    enrollment.email = request.user.email
                try:
                    enrollment.save()
                except IntegrityError:
                    messages.info(request, "You are already enrolled in this course.")
                else:
                    messages.success(request, "Enrollment successful. Welcome to the course!")
                return redirect(course.get_absolute_url())

        if action == "quiz":
            quiz_form = QuizSubmissionForm(request.POST, questions=questions)
            if quiz_form.is_valid():
                score = sum(
                    1
                    for question in questions
                    if quiz_form.cleaned_data[f"question_{question.id}"] == question.correct_answer
                )
                attempt = QuizAttempt.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    full_name=quiz_form.cleaned_data["full_name"],
                    email=quiz_form.cleaned_data["email"],
                    course=course,
                    score=score,
                    total_questions=len(questions),
                )
                messages.success(
                    request,
                    f"Quiz submitted. Your marks: {attempt.score}/{attempt.total_questions} ({attempt.percentage}%).",
                )
                return redirect(f"{course.get_absolute_url()}?email={attempt.email}#quiz")

    latest_attempt = None
    report_email = request.GET.get("email")
    if report_email:
        latest_attempt = course.quiz_attempts.filter(email__iexact=report_email).first()

    return render(
        request,
        "courses/detail.html",
        {
            "course": course,
            "enrollment_form": enrollment_form,
            "quiz_form": quiz_form,
            "questions": questions,
            "latest_attempt": latest_attempt,
            "report_email": report_email or "",
            "is_enrolled": is_enrolled,
        },
    )


def performance_report(request):
    form = ReportLookupForm(request.GET or None)
    attempts = QuizAttempt.objects.none()
    summary = None

    if form.is_valid():
        email = form.cleaned_data["email"]
        attempts = QuizAttempt.objects.filter(email__iexact=email).select_related("course")
        total_score = sum(attempt.score for attempt in attempts)
        total_questions = sum(attempt.total_questions for attempt in attempts)
        summary = {
            "email": email,
            "attempts": attempts.count(),
            "score": total_score,
            "total": total_questions,
            "percentage": round((total_score / total_questions) * 100) if total_questions else 0,
        }

    return render(
        request,
        "courses/report.html",
        {"form": form, "attempts": attempts, "summary": summary},
    )


@login_required
def quiz_session_start(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(course=course, user=request.user).exists():
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect("course_detail", slug=slug)
    
    # Get or create quiz session
    session, created = QuizSession.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'time_limit_minutes': 30}
    )
    
    if session.is_completed:
        messages.info(request, "You have already completed this quiz.")
        return redirect("quiz_session_result", slug=slug)
    
    return redirect("quiz_session_question", slug=slug)


@login_required
def quiz_session_question(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    session = get_object_or_404(QuizSession, user=request.user, course=course)
    
    if session.is_completed:
        return redirect("quiz_session_result", slug=slug)
    
    if session.is_time_expired:
        # Auto-submit when time expires
        session.is_completed = True
        session.completed_at = timezone.now()
        session.save()
        
        # Create quiz attempt record
        questions = list(course.quiz_questions.all())
        score = sum(
            1 for question in questions
            if session.answers.get(str(question.id)) == question.correct_answer
        )
        
        QuizAttempt.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            course=course,
            score=score,
            total_questions=len(questions)
        )
        
        messages.warning(request, "Time expired! Your quiz has been automatically submitted.")
        return redirect("quiz_session_result", slug=slug)
    
    current_question = session.get_next_question()
    if not current_question:
        return redirect("quiz_session_result", slug=slug)
    
    if request.method == "POST":
        answer = request.POST.get('answer')
        if answer:
            session.answers[str(current_question.id)] = answer
            session.current_question_index += 1
            session.save()
            
            if session.current_question_index >= course.quiz_questions.count():
                # Quiz completed
                session.is_completed = True
                session.completed_at = timezone.now()
                session.save()
                
                # Calculate score
                questions = list(course.quiz_questions.all())
                score = sum(
                    1 for question in questions
                    if session.answers.get(str(question.id)) == question.correct_answer
                )
                session.score = score
                session.save()
                
                # Create quiz attempt record
                QuizAttempt.objects.create(
                    user=request.user,
                    full_name=request.user.get_full_name() or request.user.username,
                    email=request.user.email,
                    course=course,
                    score=score,
                    total_questions=len(questions)
                )
                
                return redirect("quiz_session_result", slug=slug)
            else:
                return redirect("quiz_session_question", slug=slug)
    
    return render(request, "courses/quiz_session.html", {
        "course": course,
        "session": session,
        "current_question": current_question,
        "question_number": session.current_question_index + 1,
        "total_questions": course.quiz_questions.count(),
        "time_remaining": session.time_remaining_seconds
    })


@login_required
def quiz_session_result(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    session = get_object_or_404(QuizSession, user=request.user, course=course)
    
    if not session.is_completed:
        return redirect("quiz_session_question", slug=slug)
    
    questions = list(course.quiz_questions.all())
    question_results = []
    
    for i, question in enumerate(questions):
        user_answer = session.answers.get(str(question.id))
        is_correct = user_answer == question.correct_answer
        question_results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
    
    return render(request, "courses/quiz_result.html", {
        "course": course,
        "session": session,
        "question_results": question_results,
        "percentage": round((session.score / len(questions)) * 100) if questions else 0
    })


@login_required
def admin_user_verification(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("home")
    
    profiles = UserProfile.objects.all().select_related('user')
    
    if request.method == "POST":
        profile_id = request.POST.get('profile_id')
        action = request.POST.get('action')
        
        if profile_id and action:
            profile = get_object_or_404(UserProfile, id=profile_id)
            
            if action == 'verify':
                profile.is_verified = True
                profile.verification_status = 'verified'
                messages.success(request, f"User {profile.user.username} has been verified.")
            elif action == 'reject':
                profile.is_verified = False
                profile.verification_status = 'rejected'
                messages.warning(request, f"User {profile.user.username} verification has been rejected.")
            
            profile.save()
            return redirect("admin_user_verification")
    
    return render(request, "courses/admin_verification.html", {"profiles": profiles})


@login_required
def comprehensive_report(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("home")
    
    # Get comprehensive statistics
    total_users = User.objects.count()
    verified_users = UserProfile.objects.filter(is_verified=True).count()
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(is_published=True).count()
    total_enrollments = Enrollment.objects.count()
    total_quiz_attempts = QuizAttempt.objects.count()
    total_sessions = QuizSession.objects.count()
    
    # Course performance data
    course_stats = []
    for course in Course.objects.all():
        enrollments = Enrollment.objects.filter(course=course).count()
        attempts = QuizAttempt.objects.filter(course=course).count()
        course_attempts = QuizAttempt.objects.filter(course=course)
        avg_score = (
            sum(attempt.percentage for attempt in course_attempts) / attempts
            if attempts
            else 0
        )
        
        course_stats.append({
            'course': course,
            'enrollments': enrollments,
            'attempts': attempts,
            'avg_score': round(avg_score, 1)
        })
    
    # User activity data
    user_activity = []
    for user in User.objects.all():
        enrollments = Enrollment.objects.filter(user=user).count()
        attempts = QuizAttempt.objects.filter(user=user).count()
        user_attempts = QuizAttempt.objects.filter(user=user)
        avg_score = (
            sum(attempt.percentage for attempt in user_attempts) / attempts
            if attempts
            else 0
        )
        
        user_activity.append({
            'user': user,
            'enrollments': enrollments,
            'attempts': attempts,
            'avg_score': round(avg_score, 1) if avg_score else 0
        })
    
    # Recent activity
    recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')[:10]
    recent_attempts = QuizAttempt.objects.select_related('user', 'course').order_by('-submitted_at')[:10]
    
    context = {
        'total_users': total_users,
        'verified_users': verified_users,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'total_enrollments': total_enrollments,
        'total_quiz_attempts': total_quiz_attempts,
        'total_sessions': total_sessions,
        'course_stats': course_stats,
        'user_activity': user_activity,
        'recent_enrollments': recent_enrollments,
        'recent_attempts': recent_attempts,
        'verification_rate': round((verified_users / total_users * 100), 1) if total_users > 0 else 0,
    }
    
    return render(request, "courses/comprehensive_report.html", context)


# ─────────────────────────────────────────────────────────────────────────────
# INSTRUCTOR PANEL VIEWS
# ─────────────────────────────────────────────────────────────────────────────

def is_staff(user):
    """Test function for user_passes_test decorator."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_staff, login_url='login')
def instructor_dashboard(request):
    """
    Main instructor dashboard overview.
    Displays key platform statistics.
    """
    stats = {
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(is_published=True).count(),
        'draft_courses': Course.objects.filter(is_published=False).count(),
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_enrollments': Enrollment.objects.count(),
        'total_quiz_attempts': QuizAttempt.objects.count(),
        'total_sessions': LiveSession.objects.count(),
        'pending_verifications': UserProfile.objects.filter(
            verification_status='pending'
        ).count(),
    }

    # Revenue calculation
    enrollments = Enrollment.objects.select_related('course')
    total_revenue = sum(
        e.course.price for e in enrollments
    )
    stats['total_revenue'] = total_revenue

    # Recent activity
    recent_courses = Course.objects.order_by('-created_at')[:5]
    recent_enrollments = (
        Enrollment.objects.select_related('user', 'course')
        .order_by('-enrolled_at')[:8]
    )

    # Course performance
    course_performance = []
    for course in Course.objects.all()[:6]:
        enrollments_count = Enrollment.objects.filter(course=course).count()
        attempts = QuizAttempt.objects.filter(course=course)
        avg_score = attempts.aggregate(models.Avg('percentage'))['percentage__avg'] or 0
        course_performance.append({
            'course': course,
            'enrollments': enrollments_count,
            'attempts': attempts.count(),
            'avg_score': round(avg_score, 1),
        })

    context = {
        'stats': stats,
        'recent_courses': recent_courses,
        'recent_enrollments': recent_enrollments,
        'course_performance': course_performance,
    }
    return render(request, 'courses/instructor_dashboard.html', context)


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict views to staff/superusers only."""
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser)

    def handle_no_permission(self):
        messages.error(self.request, "Access denied. Staff privileges required.")
        return redirect('home')


class InstructorCourseListView(StaffRequiredMixin, ListView):
    """
    List all courses with edit/delete options.
    Supports search and filtering.
    """
    model = Course
    template_name = 'courses/instructor_course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        status = self.request.GET.get('status')

        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(summary__icontains=search_query) |
                models.Q(category__icontains=search_query)
            )
        if category:
            queryset = queryset.filter(category__iexact=category)
        if level:
            queryset = queryset.filter(level=level)
        if status == 'published':
            queryset = queryset.filter(is_published=True)
        elif status == 'draft':
            queryset = queryset.filter(is_published=False)

        return queryset.prefetch_related('enrollments', 'quiz_questions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = (
            Course.objects.values_list('category', flat=True)
            .distinct().order_by('category')
        )
        context['levels'] = Course.LEVEL_CHOICES
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_level'] = self.request.GET.get('level', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class InstructorCourseCreateView(StaffRequiredMixin, CreateView):
    """
    Create a new course.
    Auto-assigns the current user as instructor if not specified.
    Auto-generates slug from title if left blank.
    """
    model = Course
    form_class = CourseModelForm
    template_name = 'courses/instructor_course_form.html'
    success_url = None  # Set dynamically in get_success_url

    def form_valid(self, form):
        # Auto-assign instructor if not specified
        if not form.cleaned_data.get('instructor'):
            form.instance.instructor = self.request.user

        # Auto-generate slug if blank
        if not form.cleaned_data.get('slug'):
            form.instance.slug = (
                form.instance.title.lower().replace(' ', '-')
            )

        messages.success(
            self.request,
            f"Course '{form.instance.title}' has been created successfully."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('instructor_course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        context['action_url'] = reverse('instructor_course_create')
        return context


class InstructorCourseUpdateView(StaffRequiredMixin, UpdateView):
    """
    Update an existing course.
    """
    model = Course
    form_class = CourseModelForm
    template_name = 'courses/instructor_course_form.html'
    success_url = None
    slug_url_kwarg = 'slug'
    context_object_name = 'course'

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Course '{form.instance.title}' has been updated successfully."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('instructor_course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        context['action_url'] = reverse(
            'instructor_course_update', kwargs={'slug': self.object.slug}
        )
        return context


class InstructorCourseDeleteView(StaffRequiredMixin, DeleteView):
    """
    Delete a course with confirmation.
    """
    model = Course
    template_name = 'courses/instructor_course_confirm_delete.html'
    success_url = None
    slug_url_kwarg = 'slug'
    context_object_name = 'course'

    def delete(self, request, *args, **kwargs):
        course = self.get_object()
        messages.warning(
            request,
            f"Course '{course.title}' has been permanently deleted."
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('instructor_course_list')
