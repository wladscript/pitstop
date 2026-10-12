from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_admin:
            raise PermissionDenied("Acesso restrito a administradores.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
