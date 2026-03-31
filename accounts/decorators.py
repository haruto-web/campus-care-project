from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def deny_access(request, redirect_to='dashboard', message='Permission denied.'):
    messages.error(request, message)
    return redirect(redirect_to)


def teacher_owns_class(user, class_obj):
    return bool(
        getattr(user, 'is_authenticated', False)
        and getattr(user, 'role', None) == 'teacher'
        and getattr(class_obj, 'teacher_id', None) == user.id
    )


def teacher_owns_submission(user, submission):
    assignment = getattr(submission, 'assignment', None)
    class_obj = getattr(assignment, 'class_obj', None) if assignment else None
    return bool(
        class_obj
        and teacher_owns_class(user, class_obj)
    )


def teacher_teaches_student(user, student):
    return bool(
        getattr(user, 'is_authenticated', False)
        and getattr(user, 'role', None) == 'teacher'
        and user.classes_taught.filter(students=student).exists()
    )


def role_required(*roles):
    """Decorator to restrict view access to specific user roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if getattr(request.user, 'role', '').lower() not in [role.lower() for role in roles]:
                messages.error(request, 'Permission denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Restrict access to admin users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if getattr(request.user, 'role', '').lower() != 'admin':
            messages.error(request, 'Permission denied. Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    """Restrict access to superadmin users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if getattr(request.user, 'role', '').lower() != 'admin' or getattr(request.user, 'admin_role', '') != 'superadmin':
            messages.error(request, 'Permission denied. Superadmin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
