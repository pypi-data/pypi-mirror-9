django-filemanager
======================

A Django app that wraps Filemanager_ from `Core Five Labs`_, adding lots
of Djangoy goodness

Installing
----------

Install the package::

    pip install django-filemanager

Add it to your installed apps::

    INSTALLED_APPS += (
        'filemanager',
    )

Set a few config options::

    FILEMANAGER_UPLOAD_ROOT = MEDIA_ROOT + 'uploads/'
    FILEMANAGER_UPLOAD_URL = MEDIA_URL + 'uploads/'

And include its URLs::

    # in urls.py

    urlpatterns += patterns("",
        (r"^filemanager/", include("filemanager.urls")),
    )

Now, send a user to ``/filemanager/`` and they will be able to manage file
uploads on the server.

Configuring
-----------

The following options are supported:

``FILEMANAGER_UPLOAD_URL``
    The URL that uploaded files will be served from. This should be the
    ``MEDIA_URL`` with an optional suffix. The suffix should be the same as
    that used in the ``FILEMANAGER_UPLOAD_ROOT`` in most instances. For
    example::

        FILEMANAGER_UPLOAD_URL = MEDIA_URL + '/uploads/'

``FILEMANAGER_UPLOAD_ROOT``
    The directory that uploaded files should be saved to. This should be the
    ``MEDIA_ROOT`` with an optional suffix. The suffix should be the same as
    that used in the ``FILEMANAGER_UPLOAD_URL`` in most instances. For
    example::

        FILEMANAGER_UPLOAD_ROOT = MEDIA_ROOT + '/uploads/'

``FILEMANAGER_AUTH_CALLBACK``
    Either a callable, or a dotted Python import path to a callable, that
    checks if a user is authorised to use the Filemanager. Three default
    callbacks are supplied:

    * ``'filemanager.auth.allow_all'``: Allow all users to use the filemanager.
    * ``'filemanager.auth.require_staff'``: Only allow staff members (users
      with the ``staff`` attribute).
    * ``'filemanager.auth.require_superuser'``: Only allow superusers (users
      with the `superuser` attribute).

    The default is to only allow staff members.

    If you want to write your own, it must be a callable that takes a
    ``Request`` object and returns a boolean::

        # in myapp.auth
        def check_filemanager_auth(request):
            return request.user.has_perm('...'):

        # in settings.py
        FILEMANAGER_AUTH_CALLBACK = 'myapp.auth.check_filemanager_auth'

.. _Filemanager: https://github.com/simogeo/Filemanager
.. _`Core Five Labs`: http://labs.corefive.com/2009/10/30/an-open-file-manager-for-ckeditor-3-0/
