# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME as DEFAULT_REDIRECT_FIELD_NAME
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.http.response import HttpResponse
from django.utils.encoding import force_str
from django.views.static import serve as static_serve
try:
    import dajaxice.core
except ImportError:
    dajaxice = None
import re
try:
    from urllib.parse import urlparse  # Python 3
except ImportError:
    from urlparse import urlparse  # Python 2


def login_exempt(view):
    """
    Use as a decorator in the views that should be publicly accessible.
    """
    view.login_exempt_view = True
    return view


class LoginRequiredMiddleware(object):
    """
    Makes all requests require authentication. Exceptions are:
    - Views marked with the @login_exempt decorator
    - Views in the optional LOGIN_EXEMPT_URLS setting, which should be a tuple/list of URL regexes
    - Built-in admin views (which already require login), unless settings.USE_LOGIN_REQUIRED_MIDDLEWARE_FOR_ADMIN is True
      In this case, the global login page will be shown instead of the admin login page.
    - django.contrib.staticfiles.views.serve
    """
    @classmethod
    def is_exempt_match(cls, url):
        exempt_urls = getattr(cls, '__exempt_urls_cache', None)
        if exempt_urls is None:
            exempt_urls = []
            if getattr(settings, 'LOGIN_URL', None):
                exempt_urls += [re.compile(settings.LOGIN_URL.lstrip('/'))]
            if getattr(settings, 'LOGIN_ERROR_URL', None):
                exempt_urls += [re.compile(settings.LOGIN_ERROR_URL.lstrip('/'))]
            if getattr(settings, 'LOGIN_EXEMPT_URLS', None):
                exempt_urls += [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
            cls.__exempt_urls_cache = exempt_urls
        if url[0] == '/':
            url = url[1:]
        return any(m.match(url) for m in exempt_urls)
    
    def process_view(self, request, view, args, kwargs):
        if (request.user.is_authenticated()
            or getattr(view, 'login_exempt_view', False)
            or view == staticfiles_serve
            or view == static_serve
            or self.test_dajaxice(request, view, args, kwargs)
            or self.is_exempt_match(request.path)):
            return None

        if view.__module__ == 'django.contrib.admin.sites' and not getattr(settings, 'USE_LOGIN_REQUIRED_MIDDLEWARE_FOR_ADMIN', False):
            return None

        # If this is an AJAX request, return 403 with 'login required' as the response text.
        if request.is_ajax() or request.META.get('HTTP_X_REQUESTED_WITH') == 'APIClient':
            return HttpResponse('login required', status=403)

        # Copied from django.contrib.auth.decorators.user_passes_test().
        path = request.build_absolute_uri()
        # urlparse chokes on lazy objects in Python 3, force to str
        resolved_login_url = force_str(settings.LOGIN_URL)
        # If the login url is the same scheme and net location then just
        # use the path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)):
            path = request.get_full_path()
        from django.contrib.auth.views import redirect_to_login
        response = redirect_to_login(
            path, resolved_login_url, getattr(settings, 'REDIRECT_FIELD_NAME', DEFAULT_REDIRECT_FIELD_NAME))
        return response

    def test_dajaxice(self, request, view, args, kwargs):
        if not dajaxice:
            return False
        if '%s.%s' % (view.__module__, view.__name__) != 'dajaxice.views.DajaxiceRequest':
            return False
        try:
            f = dajaxice.core.dajaxice_functions.get(args[0])
            return getattr(f.function, 'login_exempt_view', False)
        except:
            return False
