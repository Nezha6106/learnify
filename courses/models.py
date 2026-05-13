from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['verification_status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    ]

    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=80)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration = models.CharField(max_length=40)
    summary = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['category']),
            models.Index(fields=['level']),
            models.Index(fields=['is_published']),
            models.Index(fields=['instructor']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    order = models.PositiveIntegerField(default=1)
    duration_minutes = models.PositiveIntegerField(default=10)
    content = models.TextField()

    class Meta:
        ordering = ["course", "order"]
        unique_together = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, related_name="materials", on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    material_url = models.URLField()
    material_type = models.CharField(max_length=60, default="Resource")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["course", "order"]
        unique_together = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Announcement(models.Model):
    course = models.ForeignKey(Course, related_name="announcements", on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class LiveSession(models.Model):
    course = models.ForeignKey(Course, related_name="live_sessions", on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    starts_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    zoom_url = models.URLField()
    meeting_id = models.CharField(max_length=80, blank=True)
    passcode = models.CharField(max_length=40, blank=True)
    host_name = models.CharField(max_length=120, default="Learnify mentor")

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(
        User,
        related_name="enrollments",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]
        unique_together = ["email", "course"]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['course']),
            models.Index(fields=['email']),
            models.Index(fields=['enrolled_at']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.course.title}"


class QuizQuestion(models.Model):
    ANSWER_CHOICES = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]

    course = models.ForeignKey(Course, related_name="quiz_questions", on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=160)
    option_b = models.CharField(max_length=160)
    option_c = models.CharField(max_length=160)
    option_d = models.CharField(max_length=160)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["course", "order"]
        unique_together = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - Question {self.order}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        User,
        related_name="quiz_attempts",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    course = models.ForeignKey(Course, related_name="quiz_attempts", on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['course']),
            models.Index(fields=['email']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['score']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.course.title} ({self.score}/{self.total_questions})"

    @property
    def percentage(self):
        if not self.total_questions:
            return 0
        return round((self.score / self.total_questions) * 100)


class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quiz_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    is_completed = models.BooleanField(default=False)
    current_question_index = models.PositiveIntegerField(default=0)
    answers = models.JSONField(default=dict, blank=True)
    score = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['user', 'course']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['course']),
            models.Index(fields=['started_at']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['user', 'course']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} Quiz Session"
    
    @property
    def is_time_expired(self):
        if self.completed_at:
            return False
        elapsed = timezone.now() - self.started_at
        return elapsed.total_seconds() > (self.time_limit_minutes * 60)
    
    @property
    def time_remaining_seconds(self):
        if self.completed_at:
            return 0
        elapsed = timezone.now() - self.started_at
        remaining = (self.time_limit_minutes * 60) - elapsed.total_seconds()
        return max(0, remaining)
    
    def get_next_question(self):
        questions = list(self.course.quiz_questions.all())
        if self.current_question_index < len(questions):
            return questions[self.current_question_index]
        return None


class StudentAnalytics(models.Model):
    """Track student engagement and performance metrics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_analytics')
    total_hours_spent = models.FloatField(default=0)
    courses_completed = models.PositiveIntegerField(default=0)
    average_quiz_score = models.FloatField(default=0)
    total_quiz_attempts = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Student Analytics'
        verbose_name_plural = 'Student Analytics'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['average_quiz_score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Analytics"
    
    @property
    def completion_rate(self):
        """Calculate course completion percentage"""
        if not self.user.enrollments.exists():
            return 0
        completed = self.courses_completed
        total = self.user.enrollments.count()
        return round((completed / total) * 100) if total > 0 else 0
    
    @property
    def performance_level(self):
        """Classify performance based on average score"""
        if self.average_quiz_score >= 90:
            return 'Excellent'
        elif self.average_quiz_score >= 80:
            return 'Very Good'
        elif self.average_quiz_score >= 70:
            return 'Good'
        elif self.average_quiz_score >= 60:
            return 'Fair'
        else:
            return 'Needs Improvement'
