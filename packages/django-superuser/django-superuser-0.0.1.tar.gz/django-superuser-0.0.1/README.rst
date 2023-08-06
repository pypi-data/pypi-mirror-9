django-superuser
================
At some point in development you wish you were just automatically logged into
the django admin as a super user. This middleware lets you do just that. As you
probably understand this also poses a security risk. To minimize the chances of
this middleware automatically logging someone in as a super user in a
production environment you will need to take some extra steps when installing.


Installation
------------
First you need enter the middleware in your setting file, it needs to be at
some line after the
``django.contrib.auth.middleware.AuthenticationMiddleware``::

    MIDDLEWARE_CLASSES = (
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'superuser.middleware.SuperUserMiddleware',
        ...
    )


You also need to have your IP listed in ``INTERNAL_IPS``, for example::

    INTERNAL_IPS = ('127.0.0.1',)


Lastly you need to make sure ``DEBUG = True`` in your settings file for the middleware to work.


Notes
-----
Note that the login page (usually ``/admin/login/``) does not log you in
automatically as a super user, this is so that you can login as a different
user if you like.  If you want to be logged in as a super user, just navigate
to any other admin view, for example ``/admin/``.
