from django.urls import path

from . import views

urlpatterns = [
    # Public pages
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    path("profile/", views.user_profile, name="user_profile"),
    path("reports/", views.performance_report, name="performance_report"),
    path("report-card/", views.student_report_card, name="student_report_card"),
    path("certificate/", views.generate_certificate, name="generate_certificate"),
    path("submit-project/", views.submit_project, name="submit_project"),

    # Verification
    path("verification-pending/", views.verification_pending, name="verification_pending"),

    # Course detail & quiz
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:slug>/quiz/start/", views.quiz_session_start, name="quiz_session_start"),
    path("courses/<slug:slug>/quiz/", views.quiz_session_question, name="quiz_session_question"),
    path("courses/<slug:slug>/quiz/result/", views.quiz_session_result, name="quiz_session_result"),

    # Django built-in admin
    path("admin-access/", views.admin_access, name="admin_access"),

    # Admin / staff views
    path("admin/verification/", views.admin_user_verification, name="admin_user_verification"),
    path("admin/comprehensive-report/", views.comprehensive_report, name="comprehensive_report"),
    path("admin/course/<slug:slug>/components/", views.manage_course_components, name="manage_course_components"),

    # ── INSTRUCTOR PANEL ──
    path("instructor-panel/", views.instructor_dashboard, name="instructor_dashboard"),
    path("instructor-panel/courses/", views.InstructorCourseListView.as_view(), name="instructor_course_list"),
    path("instructor-panel/courses/create/", views.InstructorCourseCreateView.as_view(), name="instructor_course_create"),
    path("instructor-panel/courses/<slug:slug>/update/", views.InstructorCourseUpdateView.as_view(), name="instructor_course_update"),
    path("instructor-panel/courses/<slug:slug>/delete/", views.InstructorCourseDeleteView.as_view(), name="instructor_course_delete"),

    # ── LESSON CRUD ──
    path("instructor-panel/courses/<slug:slug>/lessons/create/", views.LessonCreateView.as_view(), name="lesson_create"),
    path("instructor-panel/courses/<slug:slug>/lessons/<int:pk>/update/", views.LessonUpdateView.as_view(), name="lesson_update"),
    path("instructor-panel/courses/<slug:slug>/lessons/<int:pk>/delete/", views.LessonDeleteView.as_view(), name="lesson_delete"),

    # ── MATERIAL CRUD ──
    path("instructor-panel/courses/<slug:slug>/materials/create/", views.MaterialCreateView.as_view(), name="material_create"),
    path("instructor-panel/courses/<slug:slug>/materials/<int:pk>/update/", views.MaterialUpdateView.as_view(), name="material_update"),
    path("instructor-panel/courses/<slug:slug>/materials/<int:pk>/delete/", views.MaterialDeleteView.as_view(), name="material_delete"),

    # ── ANNOUNCEMENT CRUD ──
    path("instructor-panel/courses/<slug:slug>/announcements/create/", views.AnnouncementCreateView.as_view(), name="announcement_create"),
    path("instructor-panel/courses/<slug:slug>/announcements/<int:pk>/update/", views.AnnouncementUpdateView.as_view(), name="announcement_update"),
    path("instructor-panel/courses/<slug:slug>/announcements/<int:pk>/delete/", views.AnnouncementDeleteView.as_view(), name="announcement_delete"),

    # ── LIVE SESSION CRUD ──
    path("instructor-panel/courses/<slug:slug>/sessions/create/", views.LiveSessionCreateView.as_view(), name="session_create"),
    path("instructor-panel/courses/<slug:slug>/sessions/<int:pk>/update/", views.LiveSessionUpdateView.as_view(), name="session_update"),
    path("instructor-panel/courses/<slug:slug>/sessions/<int:pk>/delete/", views.LiveSessionDeleteView.as_view(), name="session_delete"),

    # ── QUIZ QUESTION CRUD ──
    path("instructor-panel/courses/<slug:slug>/quizzes/create-module/", views.QuizCreateView.as_view(), name="quiz_create"),
    path("instructor-panel/courses/<slug:slug>/quizzes/<int:pk>/update-module/", views.QuizUpdateView.as_view(), name="quiz_update"),
    path("instructor-panel/courses/<slug:slug>/quizzes/<int:pk>/delete-module/", views.QuizDeleteView.as_view(), name="quiz_delete"),
    path("instructor-panel/courses/<slug:slug>/quizzes/<int:quiz_pk>/questions/create/", views.QuestionCreateView.as_view(), name="question_create"),
    path("instructor-panel/courses/<slug:slug>/questions/<int:pk>/update/", views.QuestionUpdateView.as_view(), name="question_update"),
    path("instructor-panel/courses/<slug:slug>/questions/<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="question_delete"),
    path("instructor-panel/courses/<slug:slug>/quizzes/create/", views.QuizQuestionCreateView.as_view(), name="quiz_question_create"),
    path("instructor-panel/courses/<slug:slug>/quizzes/<int:pk>/update/", views.QuizQuestionUpdateView.as_view(), name="quiz_question_update"),
    path("instructor-panel/courses/<slug:slug>/quizzes/<int:pk>/delete/", views.QuizQuestionDeleteView.as_view(), name="quiz_question_delete"),
]
