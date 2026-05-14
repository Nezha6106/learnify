from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify

from .models import (
    Course, CourseMaterial, Announcement, LiveSession, Lesson,
    Enrollment, Quiz, Question, QuizQuestion, QuizSession, UserProfile,
    ProjectSubmission
)


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Your full name"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    role = forms.ChoiceField(
        required=False,
        choices=UserProfile.ROLE_CHOICES,
        initial="student",
    )

    class Meta:
        model = User
        fields = ["full_name", "username", "email", "role", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["full_name", "email"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            full_name = user.get_full_name() or user.username
            self.fields["full_name"].initial = full_name
            self.fields["email"].initial = user.email


class QuizSubmissionForm(forms.Form):
    full_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Your name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = list(questions or [])
        for question in self.questions:
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                choices=[
                    ("A", question.option_a),
                    ("B", question.option_b),
                    ("C", question.option_c),
                    ("D", question.option_d),
                ],
                widget=forms.RadioSelect,
                label=question.question,
            )


class ReportLookupForm(forms.Form):
    email = forms.EmailField(
        label="Student email",
        widget=forms.EmailInput(attrs={"placeholder": "student@example.com"}),
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'date_of_birth', 'verification_document']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'Your phone number'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class CourseSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search courses...'})
    )
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Filter by category...'})
    )
    level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Course.LEVEL_CHOICES,
        required=False
    )
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Min price'})
    )
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Max price'})
    )


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'material_file', 'material_url', 'material_type', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Material title'}),
            'material_file': forms.FileInput(attrs={'accept': '.pdf,.zip,.txt,.md,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg'}),
            'material_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'material_type': forms.TextInput(attrs={'placeholder': 'PDF, Video, Link'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('material_file') and not cleaned_data.get('material_url'):
            raise forms.ValidationError("Add either a file upload or an external URL.")
        return cleaned_data


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Announcement title'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Message content'}),
        }


class LiveSessionForm(forms.ModelForm):
    class Meta:
        model = LiveSession
        fields = ['title', 'starts_at', 'duration_minutes', 'zoom_url', 'meeting_id', 'passcode', 'host_name']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Session title'}),
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'zoom_url': forms.URLInput(attrs={'placeholder': 'https://zoom.us/j/...'}),
            'meeting_id': forms.TextInput(attrs={'placeholder': 'Meeting ID'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'order', 'duration_minutes', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Lesson title'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Lesson content...'}),
        }


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'pass_percentage', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Module 1 Quiz'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What this quiz measures'}),
            'pass_percentage': forms.NumberInput(attrs={'min': '1', 'max': '100'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'choice_a', 'choice_b', 'choice_c', 'choice_d', 'correct_answer', 'order']
        widgets = {
            'question_text': forms.TextInput(attrs={'placeholder': 'Question text'}),
            'choice_a': forms.TextInput(attrs={'placeholder': 'Option A'}),
            'choice_b': forms.TextInput(attrs={'placeholder': 'Option B'}),
            'choice_c': forms.TextInput(attrs={'placeholder': 'Option C'}),
            'choice_d': forms.TextInput(attrs={'placeholder': 'Option D'}),
        }


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'order']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Question text'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D'}),
        }


class CourseModelForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'category', 'level', 'duration',
            'duration_hours', 'summary', 'description', 'price', 'image',
            'instructor', 'is_published', 'zoom_link'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Python'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., intro-to-python'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Backend, Frontend, Data Science'
            }),
            'level': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 4 weeks, 30 hours'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'e.g., 30'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'A short summary for cards and listings'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Full course description with curriculum details'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'instructor': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'zoom_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/...'
            }),
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from title. Must be unique.',
            'summary': 'This appears on course cards and search results.',
            'image': 'Recommended: 1200x675px (16:9 ratio). Max 2MB.',
            'zoom_link': 'Optional. Main Zoom link for live sessions.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('title', ''))
        return slug

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price


class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = ['github_url', 'description']
        widgets = {
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/your-username/your-project'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Briefly describe your capstone project...'
            }),
        }


class CertificateForm(forms.Form):
    student_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Student Full Name'})
    )
    course_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Course Title'})
    )
    completion_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    instructor_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Instructor Name (optional)'})
    )
