from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import UserProfile
from .forms import StudentSignUpForm, LoginForm
from students.models import StudentProfile


def signup_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'profile', None) and request.user.profile.is_admin:
            return redirect('admin_dashboard:dashboard')
        return redirect('students:dashboard')

    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    email = form.cleaned_data['email'].lower()
                    full_name = form.cleaned_data['full_name'].strip()
                    password = form.cleaned_data['password']
                    branch = form.cleaned_data['branch']
                    year_of_study = int(form.cleaned_data['year_of_study'])

                    # Username derived from email
                    username_base = email.split('@')[0]
                    username = username_base
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{username_base}{counter}"
                        counter += 1

                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=full_name.split()[0] if full_name else '',
                        last_name=" ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else '',
                    )

                    # Create UserProfile strictly as STUDENT (Single-admin protected)
                    UserProfile.objects.create(
                        user=user,
                        role=UserProfile.ROLE_STUDENT,
                    )

                    # Create StudentProfile
                    StudentProfile.objects.create(
                        user=user,
                        full_name=full_name,
                        email=email,
                        branch=branch,
                        year_of_study=year_of_study,
                        cgpa=0.00,
                    )

                messages.success(request, f"Welcome to the platform, {full_name}! Your student account has been created.")
                login(request, user)
                # Redirect to a unified home page regardless of role
                return redirect('core:landing')
            except Exception as e:
                messages.error(request, f"An error occurred while creating your account: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = StudentSignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        # Already logged in – send to unified home
        return redirect('core:landing')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username_or_email'].strip()
            password = form.cleaned_data['password']

            # Resolve identifier to a username
            username_to_auth = identifier
            if '@' in identifier:
                user_obj = User.objects.filter(email__iexact=identifier).first()
                if user_obj:
                    username_to_auth = user_obj.username

            user = authenticate(request, username=username_to_auth, password=password)
            if user is not None:
                login(request, user)
                # Ensure a profile exists (fallback to student role)
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': UserProfile.ROLE_ADMIN if user.is_superuser else UserProfile.ROLE_STUDENT}
                )
                messages.success(request, f"Signed in successfully as {user.get_full_name() or user.username}.")
                return redirect('core:landing')
            else:
                messages.error(request, "Invalid credentials. Please verify your email/username and password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def home(request):
    """Unified home after authentication.
    Admins go to admin dashboard, students to student dashboard.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    # Ensure a UserProfile exists (fallback to student role)
    profile, _ = UserProfile.objects.get_or_create(user=request.user,
        defaults={'role': UserProfile.ROLE_STUDENT})
    if profile.is_admin or request.user.is_superuser:
        return redirect('admin_dashboard:dashboard')
    else:
        return redirect('students:dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been safely signed out.")
    return redirect('accounts:login')
