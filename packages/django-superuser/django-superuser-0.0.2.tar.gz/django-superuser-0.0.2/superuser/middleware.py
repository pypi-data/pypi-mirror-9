from .models import SuperUser
from django.conf import settings
from django.core.urlresolvers import reverse


class SuperUserMiddleware(object):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if (user is None or user.is_anonymous() and
                settings.DEBUG and
                request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and
                request.path.startswith(reverse('admin:index')) and  # we are using the admin app
                request.path != reverse('admin:login')):  # we are not on the admin login page
            request.user = SuperUser()
