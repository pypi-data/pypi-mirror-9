# -*- coding: utf-8 -*-


class ExceptionUserInfoMiddleware(object):
    """
    Adds user details to request context on receiving an exception, so that they show up in the error emails.
    Based on: https://gist.github.com/sidmitra/646372

    Add to settings.MIDDLEWARE_CLASSES and keep it outermost (i.e. on top if possible).
    This allows it to catch exceptions in other middlewares as well.
    """

    def process_exception(self, request, exception):
        try:
            if request.user.is_authenticated():
                request.META['USER_ID'] = str(request.user.id)
                request.META['USER_NAME'] = str(request.user.username)
                request.META['USER_EMAIL'] = str(request.user.email)
        except Exception as ex:
            try:
                request.META['USER_INFO'] = u"Exception raised while recording user info: %s" % ex
            except:
                request.META['USER_INFO'] = u"Exception raised while recording user info: %s" % ex.__class__
