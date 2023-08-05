# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings


def to_precision(dec, places=None, min_places=None, max_places=None, rounding=None):
    """
    Returns the given Decimal object quantized to a number of decimal places within the given range.
    If the given value has less places than min_places, it will be zero-padded.
    If the given value has more places than max_places, it will be rounded.
    If the given value is None, returns None.
    """
    if dec is None:
        return None
    dec = Decimal(dec)
    if places is None:
        if min_places is None and max_places is None:
            return dec
        places = max(-dec.normalize().as_tuple().exponent, 0)
        if max_places is not None:
            places = min(places, max_places)
        if min_places is not None:
            places = max(places, min_places)
    return dec.quantize(Decimal('%%.%df' % places % 0),
                        ROUND_HALF_UP if rounding is None else rounding)


def format_number(value, places=None, min_places=None, max_places=None, rounding=None,
                  multiplier=None, default=None, prefix=None, suffix=None, thousands_separator=None,
                  decimal_separator=None, grouping=None, postfix=None):
    """
    Returns a number formatted to a string.

    eg.:
        value: '10000.3380'
        returns: 10.000,338

    The 'grouping' parameter is an alias for 'thousands_separator' for backwards compatibility.
    The 'postfix' parameter is an alias for 'suffix' for backwards compatibility.
    
    Both 'thousands_separator' and 'decimal_separator' accept either a string or a boolean-convertible value.
    If nothing is passed, a non-string is passed and it evaluates to True, it uses the values from
    settings.DEFAULT_THOUSANDS_SEPARATOR and settings.DEFAULT_DECIMAL_SEPARATOR. In case these don't exist,
    they default to the English-language separators: '.' for decimal_separator and ',' for thousands_separator.

    """
    DEFAULT_THOUSANDS_SEPARATOR = getattr(settings, 'DEFAULT_THOUSANDS_SEPARATOR', ',')
    DEFAULT_DECIMAL_SEPARATOR = getattr(settings, 'DEFAULT_DECIMAL_SEPARATOR', '.')

    # Default parameter values.
    if value is None:
        return default
    if grouping is not None and thousands_separator is None:
        thousands_separator = grouping
    if postfix is not None and suffix is None:
        suffix = postfix
    if thousands_separator is None:
        thousands_separator = True
    if decimal_separator is None:
        decimal_separator = True
    if not isinstance(thousands_separator, basestring):
        thousands_separator = DEFAULT_THOUSANDS_SEPARATOR if thousands_separator else u""
    if not isinstance(decimal_separator, basestring):
        decimal_separator = DEFAULT_DECIMAL_SEPARATOR if decimal_separator else u""

    value = Decimal(value) * (multiplier or 1)
    value = to_precision(value, places=places, min_places=min_places, max_places=max_places, rounding=rounding)
    places = max(-value.as_tuple().exponent, 0)

    if thousands_separator:
        formatter = u'{0}{1:,.%sf}{2}' % places
    else:
        formatter = u'{0}{1:.%sf}{2}' % places
    return formatter.format(prefix or u"", value, suffix or u"") \
                    .replace(',', 'TSEP').replace('.', 'DSEP') \
                    .replace('TSEP', thousands_separator).replace('DSEP', decimal_separator)
