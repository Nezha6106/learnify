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

    # Course detail & quiz
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:slug>/quiz/start/", views.quiz_session_start, name="quiz_session_start"),
    path("courses/<slug:slug>/quiz/", views.quiz_session_question, name="quiz_session_question"),
    path("courses/<slug:slug>/quiz/result/", views.quiz_session_result, name="quiz_session_result"),

    # Django built-in admin
    path("admin-access/", views.admin_access, name="admin_access"),

    # Legacy admin views
    path("admin/verification/", views.admin_user_verification, name="admin_user_verification"),
    path("admin/comprehensive-report/", views.comprehensive_report, name="comprehensive_report"),

    # ── INSTRUCTOR PANEL ──
    path("instructor-panel/", views.instructor_dashboard, name="instructor_dashboard"),
    path("instructor-panel/courses/", views.InstructorCourseListView.as_view(), name="instructor_course_list"),
    path("instructor-panel/courses/create/", views.InstructorCourseCreateView.as_view(), name="instructor_course_create"),
    path("instructor-panel/courses/<slug:slug>/update/", views.InstructorCourseUpdateView.as_view(), name="instructor_course_update"),
    path("instructor-panel/courses/<slug:slug>/delete/", views.InstructorCourseDeleteView.as_view(), name="instructor_course_delete"),
]
