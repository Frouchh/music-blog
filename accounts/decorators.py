from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Пускает в представление только пользователей с одной из указанных ролей."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.has_role(*roles):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
