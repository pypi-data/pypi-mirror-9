# -*- coding: utf-8 -*-
from django.template import Library
from django.template.defaultfilters import escapejs
from django.utils.safestring import mark_safe
from inoa.utils.json import ExtendedJSONEncoder
import json


register = Library()

@register.filter
def as_json(value):
    """
    Encodes a variable as JSON, escapes and and wraps it with quotes and javascript-decode.
    The variable must be serializable with simplejson.
    Usage (in a JavaScript section of a template):
    var something = {{something|as_json}};
    """
    j = json.dumps(value, cls=ExtendedJSONEncoder)
    j = escapejs(j).replace('\u0022', '"')
    j = "jQuery.parseJSON('%s')" % j
    return mark_safe(j)
