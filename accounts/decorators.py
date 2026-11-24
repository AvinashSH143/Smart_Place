from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the admin portal.")
            return redirect('accounts:login')
        
        try:
            profile = request.user.profile
            if not profile.is_admin and not request.user.is_superuser:
                messages.error(request, "Access restricted to authorized platform administrators only.")
                return redirect('students:dashboard')
        except Exception:
            if not request.user.is_superuser:
                messages.error(request, "Unauthorized access.")
                return redirect('accounts:login')
                
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access your student dashboard.")
            return redirect('accounts:login')
            
        try:
            profile = request.user.profile
            if profile.is_admin:
                return redirect('admin_dashboard:dashboard')
            if not profile.is_student:
                messages.error(request, "Access restricted to registered students.")
                return redirect('accounts:login')
        except Exception:
            messages.error(request, "User profile not found. Please contact administration.")
            return redirect('accounts:login')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
