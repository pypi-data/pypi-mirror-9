from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.db import DEFAULT_DB_ALIAS


class SuperUserMiddleware(object):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if (user is None or user.is_anonymous() and
                settings.DEBUG and
                request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and
                request.path.startswith(reverse('admin:index')) and  # we are using the admin app
                request.path != reverse('admin:login')):  # we are not on the admin login page
            try:
                from django.contrib.auth import get_user_model
            except ImportError:
                from django.contrib.auth.models import User
            else:
                User = get_user_model()
            username_field = getattr(User, 'USERNAME_FIELD', 'username')
            username = 'SuperUser'
            manager = User._default_manager.db_manager(DEFAULT_DB_ALIAS)
            try:
                user = manager.get_by_natural_key(username)
            except User.DoesNotExist:
                user_data = {
                    username_field: username,
                    'is_staff': True,
                    'is_active': True,
                    'is_superuser': True,
                }
                user = manager.create(**user_data)
            user.backend = 'SuperUserBackend'
            auth.login(request, user)
