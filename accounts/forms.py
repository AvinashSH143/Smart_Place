from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile
from students.models import StudentProfile
from companies.models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'website', 'industry', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'placeholder': 'Company name'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'placeholder': 'https://company.com'}),
            'industry': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'placeholder': 'Information Technology'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm', 'rows': 3}),
        }


class StudentSignUpForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
            'placeholder': 'e.g. Alex Morgan',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
            'placeholder': 'student@university.edu',
            'autocomplete': 'email',
        })
    )
    branch = forms.ChoiceField(
        choices=StudentProfile.BRANCH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
        })
    )
    year_of_study = forms.ChoiceField(
        choices=StudentProfile.YEAR_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
        })
    )
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
            'placeholder': 'Minimum 6 characters',
            'autocomplete': 'new-password',
        })
    )
    password_confirm = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists() or StudentProfile.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
            'placeholder': 'Email address or username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm transition',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )
