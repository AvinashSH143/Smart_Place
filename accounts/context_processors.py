def user_role_context(request):
    """
    Context processor to inject role status and student profile into all templates.
    """
    if not request.user.is_authenticated:
        return {
            'is_admin_user': False,
            'is_student_user': False,
            'current_role': None,
            'current_student_profile': None,
        }

    try:
        profile = getattr(request.user, 'profile', None)
        if profile:
            is_admin = profile.is_admin or request.user.is_superuser
            is_student = profile.is_student and not request.user.is_superuser
            current_role = profile.role
        else:
            is_admin = request.user.is_superuser
            is_student = not is_admin
            current_role = 'ADMIN' if is_admin else 'STUDENT'
    except Exception:
        is_admin = request.user.is_superuser
        is_student = False
        current_role = 'ADMIN' if is_admin else 'UNKNOWN'

    student_profile = None
    if is_student and hasattr(request.user, 'student_profile'):
        student_profile = request.user.student_profile

    return {
        'is_admin_user': is_admin,
        'is_student_user': is_student,
        'current_role': current_role,
        'current_student_profile': student_profile,
    }
