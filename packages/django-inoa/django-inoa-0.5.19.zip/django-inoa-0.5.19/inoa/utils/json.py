# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime, date, time
from decimal import Decimal
from json import JSONEncoder


class ExtendedJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            exponent = obj.as_tuple()[2]
            if exponent < 0:
                return "%%.%df" % -exponent % obj
            else:
                return "%d.0" % obj
        if isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, time):
            return obj.isoformat()
        return super(ExtendedJSONEncoder, self).default(obj) 

