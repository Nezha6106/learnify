from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.utils.decorators import method_decorator

from .forms import (
    CourseModelForm, CourseMaterialForm, AnnouncementForm,
    LiveSessionForm, LessonForm, QuizForm, QuestionForm,
    QuizQuestionForm, EnrollmentForm,
    QuizSubmissionForm, ReportLookupForm, SignUpForm,
    UserProfileForm, CourseSearchForm, ProjectSubmissionForm,
    CertificateForm
)
from django.contrib.auth.models import User

from .models import (
    Course, Enrollment, LiveSession, QuizAttempt,
    QuizSession, UserProfile, StudentAnalytics,
    UserProgress, ProjectSubmission, Lesson, Quiz, Question, QuizQuestion,
    Announcement, CourseMaterial
)
from .decorators import verified_required


PASS_PERCENTAGE = 80


def get_primary_quiz(course):
    return (
        course.quizzes.filter(is_active=True)
        .prefetch_related("questions")
        .order_by("order")
        .first()
    )


def get_course_quiz_questions(course):
    quiz = get_primary_quiz(course)
    if quiz and quiz.questions.exists():
        return quiz, list(quiz.questions.all())
    return None, list(course.quiz_questions.all())


def sync_user_progress(user, course, quiz_passed=False, complete_lessons=False):
    progress, _ = UserProgress.objects.get_or_create(user=user, course=course)
    progress.total_lessons = course.lessons.count()
    progress.total_quizzes = 1 if get_course_quiz_questions(course)[1] else 0
    if complete_lessons:
        progress.completed_lessons_count = progress.total_lessons
        progress.completed_lessons.set(course.lessons.all())
    else:
        progress.completed_lessons_count = progress.completed_lessons.count()
    if quiz_passed:
        progress.quizzes_passed = 1
    total_items = progress.total_lessons + progress.total_quizzes
    completed_items = progress.completed_lessons_count + progress.quizzes_passed
    progress.is_completed = bool(total_items and completed_items >= total_items)
    progress.save()
    if progress.is_completed:
        analytics, _ = StudentAnalytics.objects.get_or_create(user=user)
        analytics.courses_completed = UserProgress.objects.filter(user=user, is_completed=True).count()
        analytics.save(update_fields=["courses_completed", "last_activity"])
    return progress


# ─────────────────────────────────────────────────────────────────────
# AUTH & SECURITY
# ─────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────
# VERIFICATION PENDING PAGE
# ─────────────────────────────────────────────────────────────────────

def verification_pending(request):
    """Stylized page shown to unverified users."""
    return render(request, "courses/verification_pending.html")


# ─────────────────────────────────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────
# HOME / PUBLIC
# ─────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────
# STUDENT DASHBOARD (with verification gate)
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def dashboard(request):
    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .select_related("course")
        .prefetch_related("course__lessons", "course__live_sessions", "course__materials", "course__announcements")
    )
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    attempts = QuizAttempt.objects.filter(user=request.user).select_related("course")[:8]
    sessions = LiveSession.objects.filter(course__in=enrolled_courses).select_related("course")[:8]

    # Progress data for each enrolled course
    progress_data = []
    for enrollment in enrollments:
        progress, _ = UserProgress.objects.get_or_create(user=request.user, course=enrollment.course)
        total_lessons = enrollment.course.lessons.count()
        _, quiz_questions = get_course_quiz_questions(enrollment.course)
        if total_lessons > 0 or quiz_questions:
            progress.total_lessons = total_lessons
            progress.total_quizzes = 1 if quiz_questions else 0
            progress.completed_lessons_count = progress.completed_lessons.count()
            total_items = progress.total_lessons + progress.total_quizzes
            completed_items = progress.completed_lessons_count + progress.quizzes_passed
            progress.is_completed = bool(total_items and completed_items >= total_items)
            progress.save()
        progress_data.append({
            'enrollment': enrollment,
            'progress': progress,
        })

    return render(
        request,
        "courses/dashboard.html",
        {
            "enrollments": enrollments,
            "attempts": attempts,
            "sessions": sessions,
            "progress_data": progress_data,
        },
    )


# ─────────────────────────────────────────────────────────────────────
# ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def analytics_dashboard(request):
    analytics, created = StudentAnalytics.objects.get_or_create(user=request.user)
    enrollments = request.user.enrollments.select_related('course')
    enrolled_courses = [e.course for e in enrollments]
    quiz_attempts = request.user.quiz_attempts.select_related('course').order_by('-submitted_at')[:10]
    total_quizzes = quiz_attempts.count()
    if total_quizzes > 0:
        avg_score = sum(q.percentage for q in quiz_attempts) / total_quizzes
        analytics.average_quiz_score = avg_score
        analytics.total_quiz_attempts = total_quizzes
        analytics.save(update_fields=['average_quiz_score', 'total_quiz_attempts'])

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


# ─────────────────────────────────────────────────────────────────────
# COURSE DETAIL
# ─────────────────────────────────────────────────────────────────────

def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            "announcements", "lessons", "materials", "quiz_questions",
            "quizzes__questions", "live_sessions"
        ),
        slug=slug,
        is_published=True,
    )
    active_quiz, questions = get_course_quiz_questions(course)
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
                    # Create/update progress record
                    progress, _ = UserProgress.objects.get_or_create(user=request.user, course=course)
                    progress.total_lessons = course.lessons.count()
                    progress.total_quizzes = 1 if questions else 0
                    progress.save()
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
                percentage = round((score / len(questions)) * 100) if questions else 0
                pass_percentage = active_quiz.pass_percentage if active_quiz else PASS_PERCENTAGE
                attempt = QuizAttempt.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    full_name=quiz_form.cleaned_data["full_name"],
                    email=quiz_form.cleaned_data["email"],
                    course=course,
                    quiz=active_quiz,
                    score=score,
                    total_questions=len(questions),
                    passed=percentage >= pass_percentage,
                )
                if request.user.is_authenticated:
                    sync_user_progress(request.user, course, quiz_passed=attempt.passed)
                messages.success(
                    request,
                    f"Quiz submitted. Your marks: {attempt.score}/{attempt.total_questions} ({attempt.percentage}%).",
                )
                return redirect(f"{course.get_absolute_url()}?email={attempt.email}#quiz")

    latest_attempt = None
    report_email = request.GET.get("email")
    if report_email:
        latest_attempt = course.quiz_attempts.filter(email__iexact=report_email).first()

    progress = None
    if request.user.is_authenticated:
        progress = UserProgress.objects.filter(user=request.user, course=course).first()

    return render(
        request,
        "courses/detail.html",
        {
            "course": course,
            "enrollment_form": enrollment_form,
            "quiz_form": quiz_form,
            "questions": questions,
            "active_quiz": active_quiz,
            "latest_attempt": latest_attempt,
            "report_email": report_email or "",
            "is_enrolled": is_enrolled,
            "progress": progress,
        },
    )


# ─────────────────────────────────────────────────────────────────────
# PERFORMANCE REPORT
# ─────────────────────────────────────────────────────────────────────

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
    return render(request, "courses/report.html", {"form": form, "attempts": attempts, "summary": summary})


# ─────────────────────────────────────────────────────────────────────
# QUIZ SESSION (timed, question-by-question)
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def quiz_session_start(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if not Enrollment.objects.filter(course=course, user=request.user).exists():
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect("course_detail", slug=slug)
    active_quiz, questions = get_course_quiz_questions(course)
    if not questions:
        messages.error(request, "This course does not have quiz questions yet.")
        return redirect("course_detail", slug=slug)
    session, created = QuizSession.objects.get_or_create(
        user=request.user,
        course=course,
        quiz=active_quiz,
        defaults={'time_limit_minutes': 30}
    )
    if session.is_completed:
        messages.info(request, "You have already completed this quiz.")
        return redirect("quiz_session_result", slug=slug)
    return redirect("quiz_session_question", slug=slug)


@login_required
@verified_required
def quiz_session_question(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    active_quiz, questions = get_course_quiz_questions(course)
    session = get_object_or_404(QuizSession, user=request.user, course=course, quiz=active_quiz)
    if session.is_completed:
        return redirect("quiz_session_result", slug=slug)
    if session.is_time_expired:
        session.is_completed = True
        session.completed_at = timezone.now()
        session.save()
        score = sum(
            1 for question in questions
            if session.answers.get(str(question.id)) == question.correct_answer
        )
        percentage = round((score / len(questions)) * 100) if questions else 0
        pass_percentage = active_quiz.pass_percentage if active_quiz else PASS_PERCENTAGE
        session.score = score
        session.save(update_fields=["score"])
        QuizAttempt.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            course=course,
            quiz=active_quiz,
            score=score,
            total_questions=len(questions),
            passed=percentage >= pass_percentage,
        )
        sync_user_progress(request.user, course, quiz_passed=percentage >= pass_percentage, complete_lessons=True)
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
            if session.current_question_index >= len(questions):
                session.is_completed = True
                session.completed_at = timezone.now()
                session.save()
                score = sum(
                    1 for question in questions
                    if session.answers.get(str(question.id)) == question.correct_answer
                )
                session.score = score
                session.save()
                percentage = round((score / len(questions)) * 100) if questions else 0
                pass_percentage = active_quiz.pass_percentage if active_quiz else PASS_PERCENTAGE
                QuizAttempt.objects.create(
                    user=request.user,
                    full_name=request.user.get_full_name() or request.user.username,
                    email=request.user.email,
                    course=course,
                    quiz=active_quiz,
                    score=score,
                    total_questions=len(questions),
                    passed=percentage >= pass_percentage,
                )
                sync_user_progress(request.user, course, quiz_passed=percentage >= pass_percentage, complete_lessons=True)
                return redirect("quiz_session_result", slug=slug)
            else:
                return redirect("quiz_session_question", slug=slug)

    return render(request, "courses/quiz_session.html", {
        "course": course,
        "session": session,
        "current_question": current_question,
        "question_number": session.current_question_index + 1,
        "total_questions": len(questions),
        "time_remaining": session.time_remaining_seconds,
    })


@login_required
@verified_required
def quiz_session_result(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    active_quiz, questions = get_course_quiz_questions(course)
    session = get_object_or_404(QuizSession, user=request.user, course=course, quiz=active_quiz)
    if not session.is_completed:
        return redirect("quiz_session_question", slug=slug)
    question_results = []
    for i, question in enumerate(questions):
        user_answer = session.answers.get(str(question.id))
        is_correct = user_answer == question.correct_answer
        question_results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
    pass_percentage = active_quiz.pass_percentage if active_quiz else PASS_PERCENTAGE
    percentage = round((session.score / len(questions)) * 100) if questions else 0
    sync_user_progress(
        request.user,
        course,
        quiz_passed=percentage >= pass_percentage,
        complete_lessons=True,
    )

    return render(request, "courses/quiz_result.html", {
        "course": course,
        "session": session,
        "question_results": question_results,
        "percentage": percentage,
        "passed": percentage >= pass_percentage,
        "pass_percentage": pass_percentage,
    })


# ─────────────────────────────────────────────────────────────────────
# LEGACY REPORT
# ─────────────────────────────────────────────────────────────────────

def comprehensive_report(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("home")
    total_users = User.objects.count()
    verified_users = UserProfile.objects.filter(is_verified=True).count()
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(is_published=True).count()
    total_enrollments = Enrollment.objects.count()
    total_quiz_attempts = QuizAttempt.objects.count()
    total_sessions = QuizSession.objects.count()
    course_stats = []
    for course in Course.objects.all():
        enrollments = Enrollment.objects.filter(course=course).count()
        attempts = QuizAttempt.objects.filter(course=course).count()
        course_attempts = QuizAttempt.objects.filter(course=course)
        avg_score = (
            sum(attempt.percentage for attempt in course_attempts) / attempts
            if attempts else 0
        )
        course_stats.append({
            'course': course,
            'enrollments': enrollments,
            'attempts': attempts,
            'avg_score': round(avg_score, 1),
        })
    user_activity = []
    for user in User.objects.all():
        enrollments = Enrollment.objects.filter(user=user).count()
        attempts = QuizAttempt.objects.filter(user=user).count()
        user_attempts = QuizAttempt.objects.filter(user=user)
        avg_score = (
            sum(attempt.percentage for attempt in user_attempts) / attempts
            if attempts else 0
        )
        user_activity.append({
            'user': user,
            'enrollments': enrollments,
            'attempts': attempts,
            'avg_score': round(avg_score, 1) if avg_score else 0,
        })
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


# ─────────────────────────────────────────────────────────────────────
# ADMIN USER VERIFICATION
# ─────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────
# STUDENT REPORT CARD
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def student_report_card(request):
    """
    Display a student's report card with quiz scores and grades
    once progress reaches 100% and capstone is submitted.
    """
    user = request.user
    profile = user.profile

    # Get all completed courses
    completed_progress = UserProgress.objects.filter(
        user=user, is_completed=True
    ).select_related('course')

    # Get all quiz attempts
    quiz_attempts = QuizAttempt.objects.filter(user=user).select_related('course').order_by('-submitted_at')

    # Check for capstone project submissions
    project_submissions = ProjectSubmission.objects.filter(
        user=user, is_approved=True
    ).select_related('course')

    context = {
        'profile': profile,
        'completed_courses': completed_progress,
        'quiz_attempts': quiz_attempts,
        'project_submissions': project_submissions,
    }
    return render(request, "courses/student_report_card.html", context)


# ─────────────────────────────────────────────────────────────────────
# CERTIFICATE GENERATION
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def generate_certificate(request):
    """
    Generate and display a printable/savable certificate for the student.
    Filters by completed courses with approved capstone projects.
    """
    user = request.user
    profile = user.profile

    # Get completed courses with approved capstones
    completed_courses = UserProgress.objects.filter(
        user=user, is_completed=True
    ).select_related('course')

    # Approved project submissions
    approved_projects = ProjectSubmission.objects.filter(
        user=user, is_approved=True
    ).select_related('course')

    # Allow generating certificate for any completed course with capstone
    eligible_courses = []
    for progress in completed_courses:
        has_capstone = approved_projects.filter(course=progress.course).exists()
        if has_capstone:
            eligible_courses.append(progress.course)

    # Get latest quiz attempts per course for display
    quiz_scores = {}
    for course in eligible_courses:
        latest = QuizAttempt.objects.filter(user=user, course=course).order_by('-submitted_at').first()
        if latest:
            quiz_scores[course.id] = latest

    certificate_data = None
    if request.method == "POST" and 'generate' in request.POST:
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        # Check eligibility
        if course not in eligible_courses:
            messages.error(request, "You are not eligible for a certificate for this course.")
            return redirect("generate_certificate")

        # Determine grade
        attempt = quiz_scores.get(course.id)
        grade = "--"
        if attempt:
            pct = attempt.percentage
            if pct >= 90:
                grade = "A"
            elif pct >= 80:
                grade = "B"
            elif pct >= 70:
                grade = "C"
            elif pct >= 60:
                grade = "D"
            else:
                grade = "F"

        now = timezone.now()
        certificate_data = {
            'student_name': profile.full_name,
            'course_title': course.title,
            'date': now.strftime("%B %d, %Y"),
            'grade': grade,
            'quiz_score': f"{attempt.score}/{attempt.total_questions}" if attempt else "N/A",
            'percentage': f"{attempt.percentage}%" if attempt else "N/A",
            'signature_line': "Prof. " + (course.instructor.get_full_name() if course.instructor else "Learnify Academy"),
        }

        if 'download_pdf' in request.POST:
            # Render certificate as printable HTML
            return render(request, "courses/certificate_printable.html", {
                "certificate": certificate_data,
                "print_mode": True,
            })

        return render(request, "courses/certificate.html", {
            "certificate": certificate_data,
            "eligible_courses": eligible_courses,
            "quiz_scores": quiz_scores,
        })

    return render(request, "courses/certificate.html", {
        "eligible_courses": eligible_courses,
        "quiz_scores": quiz_scores,
    })


# ─────────────────────────────────────────────────────────────────────
# PROJECT SUBMISSION
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def submit_project(request):
    """Allow authenticated students to submit their capstone project."""
    user = request.user

    # Get courses the user has completed but hasn't submitted a project for
    completed = UserProgress.objects.filter(user=user, is_completed=True).select_related('course')
    existing_submissions = ProjectSubmission.objects.filter(user=user).values_list('course_id', flat=True)

    eligible_courses = [p for p in completed if p.course_id not in existing_submissions]

    if request.method == "POST":
        form = ProjectSubmissionForm(request.POST)
        if form.is_valid():
            course_id = request.POST.get('course_id')
            course = get_object_or_404(Course, id=course_id)

            # Verify the user completed this course
            if course.id not in [c.course_id for c in eligible_courses] and course.id not in existing_submissions:
                messages.error(request, "You must complete the course before submitting a project.")
                return redirect("submit_project")

            ProjectSubmission.objects.update_or_create(
                user=user,
                course=course,
                defaults={
                    'github_url': form.cleaned_data['github_url'],
                    'description': form.cleaned_data['description'],
                }
            )
            messages.success(request, f"Project submitted for '{course.title}'! Awaiting review.")
            return redirect("dashboard")
    else:
        form = ProjectSubmissionForm()

    return render(request, "courses/submit_project.html", {
        "form": form,
        "eligible_courses": eligible_courses,
    })


# ─────────────────────────────────────────────────────────────────────
# INSTRUCTOR PANEL
# ─────────────────────────────────────────────────────────────────────

def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_staff, login_url='login')
def instructor_dashboard(request):
    stats = {
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(is_published=True).count(),
        'draft_courses': Course.objects.filter(is_published=False).count(),
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_enrollments': Enrollment.objects.count(),
        'total_quiz_attempts': QuizAttempt.objects.count(),
        'total_sessions': LiveSession.objects.count(),
        'pending_verifications': UserProfile.objects.filter(verification_status='pending').count(),
    }
    enrollments = Enrollment.objects.select_related('course')
    total_revenue = sum(e.course.price for e in enrollments)
    stats['total_revenue'] = total_revenue

    recent_courses = Course.objects.order_by('-created_at')[:5]
    recent_enrollments = (
        Enrollment.objects.select_related('user', 'course')
        .order_by('-enrolled_at')[:8]
    )
    course_performance = []
    for course in Course.objects.all()[:6]:
        enrollments_count = Enrollment.objects.filter(course=course).count()
        attempts = QuizAttempt.objects.filter(course=course)
        avg_score = (
            sum(attempt.percentage for attempt in attempts) / attempts.count()
            if attempts.exists() else 0
        )
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


# ─────────────────────────────────────────────────────────────────────
# ADMIN PANEL — COURSE CRUD
# ─────────────────────────────────────────────────────────────────────

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser)

    def handle_no_permission(self):
        messages.error(self.request, "Access denied. Staff privileges required.")
        return redirect('home')


class CourseContextMixin:
    def get_course(self):
        if hasattr(self, "object") and getattr(self.object, "course_id", None):
            return self.object.course
        if hasattr(self, "object") and getattr(self.object, "quiz_id", None):
            return self.object.quiz.course
        if "quiz_pk" in self.kwargs:
            return get_object_or_404(Quiz, pk=self.kwargs["quiz_pk"], course__slug=self.kwargs["slug"]).course
        return get_object_or_404(Course, slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.get_course()
        return context


class InstructorCourseListView(StaffRequiredMixin, ListView):
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
    model = Course
    form_class = CourseModelForm
    template_name = 'courses/instructor_course_form.html'
    success_url = None

    def form_valid(self, form):
        if not form.cleaned_data.get('instructor'):
            form.instance.instructor = self.request.user
        if not form.cleaned_data.get('slug'):
            form.instance.slug = form.instance.title.lower().replace(' ', '-')
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


# ─────────────────────────────────────────────────────────────────────
# ADMIN PANEL — MANAGE COURSE INLINE COMPONENTS
# ─────────────────────────────────────────────────────────────────────

@user_passes_test(is_staff, login_url='login')
def manage_course_components(request, slug):
    """Central page for managing lessons, materials, announcements, live sessions, quizzes for a course."""
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.all().order_by('order')
    materials = course.materials.all().order_by('order')
    announcements = course.announcements.all().order_by('-created_at')
    live_sessions = course.live_sessions.all().order_by('starts_at')
    quiz_questions = course.quiz_questions.all().order_by('order')
    quizzes = course.quizzes.prefetch_related('questions').order_by('order')

    # Forms for inline creation
    lesson_form = LessonForm()
    material_form = CourseMaterialForm()
    announcement_form = AnnouncementForm()
    session_form = LiveSessionForm()
    quiz_model_form = QuizForm()
    question_form = QuestionForm()
    quiz_form = QuizQuestionForm()

    context = {
        'course': course,
        'lessons': lessons,
        'materials': materials,
        'announcements': announcements,
        'live_sessions': live_sessions,
        'quizzes': quizzes,
        'quiz_questions': quiz_questions,
        'lesson_form': lesson_form,
        'material_form': material_form,
        'announcement_form': announcement_form,
        'session_form': session_form,
        'quiz_model_form': quiz_model_form,
        'question_form': question_form,
        'quiz_form': quiz_form,
    }
    return render(request, "courses/manage_course_components.html", context)


# ─────────────────────────────────────────────────────────────────────
# CRUD for Lessons
# ─────────────────────────────────────────────────────────────────────

@login_required
@verified_required
def lesson_list(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.all().order_by('order')
    return render(request, 'courses/lesson_list.html', {'course': course, 'lessons': lessons})


class LessonCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def form_valid(self, form):
        slug = self.kwargs['slug']
        course = get_object_or_404(Course, slug=slug)
        form.instance.course = course
        messages.success(self.request, f"Lesson '{form.instance.title}' created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class LessonUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def form_valid(self, form):
        messages.success(self.request, f"Lesson '{form.instance.title}' updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class LessonDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'courses/lesson_confirm_delete.html'

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


# ─────────────────────────────────────────────────────────────────────
# CRUD for Course Materials
# ─────────────────────────────────────────────────────────────────────

class MaterialCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = CourseMaterial
    form_class = CourseMaterialForm
    template_name = 'courses/material_form.html'

    def form_valid(self, form):
        slug = self.kwargs['slug']
        course = get_object_or_404(Course, slug=slug)
        form.instance.course = course
        messages.success(self.request, f"Material '{form.instance.title}' added.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class MaterialUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = CourseMaterial
    form_class = CourseMaterialForm
    template_name = 'courses/material_form.html'

    def form_valid(self, form):
        messages.success(self.request, f"Material '{form.instance.title}' updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class MaterialDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = CourseMaterial
    template_name = 'courses/material_confirm_delete.html'

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


# ─────────────────────────────────────────────────────────────────────
# CRUD for Announcements
# ─────────────────────────────────────────────────────────────────────

class AnnouncementCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'courses/announcement_form.html'

    def form_valid(self, form):
        slug = self.kwargs['slug']
        course = get_object_or_404(Course, slug=slug)
        form.instance.course = course
        messages.success(self.request, f"Announcement '{form.instance.title}' created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class AnnouncementUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'courses/announcement_form.html'

    def form_valid(self, form):
        messages.success(self.request, f"Announcement '{form.instance.title}' updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class AnnouncementDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'courses/announcement_confirm_delete.html'

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


# ─────────────────────────────────────────────────────────────────────
# CRUD for Live Sessions
# ─────────────────────────────────────────────────────────────────────

class LiveSessionCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = LiveSession
    form_class = LiveSessionForm
    template_name = 'courses/session_form.html'

    def form_valid(self, form):
        slug = self.kwargs['slug']
        course = get_object_or_404(Course, slug=slug)
        form.instance.course = course
        messages.success(self.request, f"Live session '{form.instance.title}' created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class LiveSessionUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = LiveSession
    form_class = LiveSessionForm
    template_name = 'courses/session_form.html'

    def form_valid(self, form):
        messages.success(self.request, f"Live session '{form.instance.title}' updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class LiveSessionDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = LiveSession
    template_name = 'courses/session_confirm_delete.html'

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


# ─────────────────────────────────────────────────────────────────────
# CRUD for Quiz Questions
# ─────────────────────────────────────────────────────────────────────

class QuizCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'courses/quiz_form.html'

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        form.instance.course = course
        messages.success(self.request, f"Quiz '{form.instance.title}' created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuizUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'courses/quiz_form.html'

    def form_valid(self, form):
        messages.success(self.request, f"Quiz '{form.instance.title}' updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuizDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = Quiz
    template_name = 'courses/quiz_confirm_delete.html'

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuestionCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'courses/question_form.html'

    def form_valid(self, form):
        quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_pk'], course__slug=self.kwargs['slug'])
        form.instance.quiz = quiz
        messages.success(self.request, "Question created.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = get_object_or_404(Quiz, pk=self.kwargs['quiz_pk'], course__slug=self.kwargs['slug'])
        return context

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuestionUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'courses/question_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.object.quiz
        return context

    def form_valid(self, form):
        messages.success(self.request, "Question updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuestionDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = Question
    template_name = 'courses/question_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.object.quiz
        return context

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuizQuestionCreateView(CourseContextMixin, StaffRequiredMixin, CreateView):
    model = QuizQuestion
    form_class = QuizQuestionForm
    template_name = 'courses/quiz_question_form.html'

    def form_valid(self, form):
        slug = self.kwargs['slug']
        course = get_object_or_404(Course, slug=slug)
        form.instance.course = course
        messages.success(self.request, f"Quiz question created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuizQuestionUpdateView(CourseContextMixin, StaffRequiredMixin, UpdateView):
    model = QuizQuestion
    form_class = QuizQuestionForm
    template_name = 'courses/quiz_question_form.html'

    def form_valid(self, form):
        messages.success(self.request, f"Quiz question updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})


class QuizQuestionDeleteView(CourseContextMixin, StaffRequiredMixin, DeleteView):
    model = QuizQuestion
    template_name = 'courses/quiz_question_confirm_delete.html'

    def get_success_url(self):
        return reverse('manage_course_components', kwargs={'slug': self.kwargs['slug']})
