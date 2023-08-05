# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
from django.http import HttpResponse
from inoa.utils.json import ExtendedJSONEncoder
import json
import django

class HttpResponseNoContent(HttpResponse):
    """
    HTTP response for a success request.
    """
    status_code = 204

def JsonResponse(data, json_cls=None, response_cls=None):
    """
    Returns an HttpResponse with JSON content type. Converts the data parameter to JSON automatically.
    Accepts two optional parameters.
    - json_cls: a subclass of simplejson.JSONEncoder
    - response_cls: a subclass of django.http.HttpResponse
    """
    json_cls = json_cls or ExtendedJSONEncoder
    response_cls = response_cls or HttpResponse
    if StrictVersion(django.get_version()) >= StrictVersion('1.7'):
        # Mimetype is not an argument anymore for HttpResponse in Django 1.7+
        kwargs = {'content_type': "application/json"}
    else:
        # For older versions of Django (1.7-)
        kwargs = {'mimetype': "application/json"}
    return response_cls(json.dumps(data, cls=json_cls), **kwargs)
