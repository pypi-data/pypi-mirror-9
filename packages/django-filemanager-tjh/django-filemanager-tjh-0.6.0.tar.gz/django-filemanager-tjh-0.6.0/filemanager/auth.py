def allow_all(request):
    return True


def require_staff(request):
    return request.user.is_staff


def require_superuser(request):
    return request.user.is_superuser
