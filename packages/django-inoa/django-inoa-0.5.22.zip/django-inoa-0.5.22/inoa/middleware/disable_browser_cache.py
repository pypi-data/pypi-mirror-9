# -*- coding: utf-8 -*-
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.views.static import serve as static_serve


class DisableBrowserCacheMiddleware(object):
    """
    Disables browser cache for all views but staticfiles.
    """
    def process_view(self, request, view, args, kwargs):
        request.is_static_view = (view == staticfiles_serve or view == static_serve)

    def process_response(self, request, response):
        if not getattr(request, 'is_static_view', True):
            response['Pragma'] = 'no-cache'
            response['Cache-Control'] = 'no-cache must-revalidate proxy-revalidate'
        return response
