from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Course, Enrollment, LiveSession, UserProfile


class LmsFlowTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Django Web Apps",
            slug="django-web-apps",
            category="Backend",
            level="Beginner",
            duration="4 weeks",
            summary="Build Django apps.",
            description="Create views, templates, and data models.",
            price=0,
        )
        self.session = LiveSession.objects.create(
            course=self.course,
            title="Zoom orientation",
            starts_at=timezone.now(),
            zoom_url="https://zoom.us/j/12345678901",
            meeting_id="123 4567 8901",
            passcode="learn",
        )

    def test_signup_creates_account(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "student",
                "email": "student@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="student", email="student@example.com").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="student", is_verified=False).exists())

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_authenticated_user_can_enroll_and_see_zoom_dashboard(self):
        user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123!",
        )
        UserProfile.objects.create(user=user, is_verified=True, verification_status="verified")
        self.client.force_login(user)

        response = self.client.post(
            self.course.get_absolute_url(),
            {
                "action": "enroll",
                "full_name": "Student",
                "email": "student@example.com",
            },
        )

        self.assertRedirects(response, self.course.get_absolute_url())
        self.assertTrue(Enrollment.objects.filter(user=user, course=self.course).exists())

        dashboard = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard, self.course.title)
        self.assertContains(dashboard, self.session.title)
        self.assertContains(dashboard, self.session.zoom_url)
