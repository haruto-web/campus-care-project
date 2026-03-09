from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Decorator to restrict view access to specific user roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, 'Permission denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_admin_role(*allowed_roles):
    """
    Restricts admin views by admin_role tier.
    Tiers: 'superadmin', 'admin', 'registrar', 'data_viewer'
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role != 'admin':
                return redirect('dashboard')
            if request.user.admin_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
