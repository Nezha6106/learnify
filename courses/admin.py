from django.contrib import admin

from .models import Announcement, Course, CourseMaterial, Enrollment, Lesson, LiveSession, QuizAttempt, QuizQuestion, UserProfile, QuizSession, StudentAnalytics


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 1


class AnnouncementInline(admin.TabularInline):
    model = Announcement
    extra = 1


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1


class LiveSessionInline(admin.TabularInline):
    model = LiveSession
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "duration", "price", "is_published")
    list_filter = ("category", "level", "is_published")
    search_fields = ("title", "summary", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [AnnouncementInline, LessonInline, CourseMaterialInline, LiveSessionInline, QuizQuestionInline]


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "material_type", "order")
    list_filter = ("course", "material_type")
    search_fields = ("title", "course__title", "material_url")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    list_filter = ("course", "created_at")
    search_fields = ("title", "message", "course__title")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "course", "user", "enrolled_at")
    list_filter = ("course", "enrolled_at")
    search_fields = ("full_name", "email", "course__title", "user__username")


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "starts_at", "duration_minutes", "host_name")
    list_filter = ("course", "starts_at")
    search_fields = ("title", "course__title", "meeting_id", "host_name")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "course", "user", "score", "total_questions", "submitted_at")
    list_filter = ("course", "submitted_at")
    search_fields = ("full_name", "email", "course__title")
    readonly_fields = ("submitted_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_verified", "verification_status", "created_at")
    list_filter = ("role", "is_verified", "verification_status", "created_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    list_editable = ("role", "is_verified", "verification_status")
    readonly_fields = ("created_at", "updated_at")


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "is_completed", "score", "started_at", "completed_at")
    list_filter = ("course", "is_completed", "started_at")
    search_fields = ("user__username", "course__title")
    readonly_fields = ("started_at",)


@admin.register(StudentAnalytics)
class StudentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("user", "average_quiz_score", "total_quiz_attempts", "courses_completed", "total_hours_spent", "last_activity")
    list_filter = ("created_at", "last_activity", "average_quiz_score")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "last_activity")
    fields = ("user", "average_quiz_score", "total_quiz_attempts", "courses_completed", "total_hours_spent", "created_at", "last_activity")
