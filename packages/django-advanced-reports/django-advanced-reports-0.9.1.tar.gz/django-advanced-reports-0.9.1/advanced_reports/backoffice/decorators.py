from functools import wraps
from django.utils.translation import ugettext as _
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME

def staff_member_required(backoffice):
    def decorate(view_func):
        """
        Decorator for views that checks that the user is logged in and is a staff
        member, displaying the login page if necessary.
        """
        @wraps(view_func)
        def _checklogin(request, *args, **kwargs):
            if request.user.is_active and request.user.is_staff:
                # The user is valid. Continue to the admin page.
                return view_func(request, *args, **kwargs)

            assert hasattr(request, 'session'), "Advanced Reports Backoffice requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
            defaults = {
                'template_name': backoffice.login_template,
                'authentication_form': AdminAuthenticationForm,
                'extra_context': {
                    'backoffice': backoffice,
                    REDIRECT_FIELD_NAME: request.get_full_path(),
                },
            }
            return login(request, **defaults)
        return _checklogin
    return decorate
