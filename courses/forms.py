from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Enrollment, UserProfile, Course


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Your full name"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    role = forms.ChoiceField(
        required=True,
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


class CourseModelForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'category', 'level', 'duration',
            'summary', 'description', 'price', 'image',
            'instructor', 'is_published'
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
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from title. Must be unique.',
            'summary': 'This appears on course cards and search results.',
            'image': 'Recommended: 1200x675px (16:9 ratio). Max 2MB.',
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = self.cleaned_data.get('title', '').lower().replace(' ', '-')
        return slug

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price
