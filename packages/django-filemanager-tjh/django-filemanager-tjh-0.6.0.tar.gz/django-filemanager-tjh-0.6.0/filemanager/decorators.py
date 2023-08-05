from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.module_loading import import_string
from django.utils.six import string_types
from functools import wraps


auth_callback = getattr(settings, 'FILEMANAGER_AUTH_CALLBACK',
                        'filemanager.auth.require_staff')

if isinstance(auth_callback, string_types):
    auth_callback = import_string(auth_callback)


def filemanager_require_auth(fn):
    @wraps(fn)
    def view(request, *args, **kwargs):
        if auth_callback(request):
            return fn(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return view
