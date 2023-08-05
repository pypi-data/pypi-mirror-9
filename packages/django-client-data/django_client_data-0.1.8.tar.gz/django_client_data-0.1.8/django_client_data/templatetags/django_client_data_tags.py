import datetime
import json

from django import template
from django.template.defaultfilters import date
from django.template.defaultfilters import time
from django.utils.safestring import mark_safe


register = template.Library()


def to_string_for_json(obj):
    # Convert date objects with Django's date filter
    if isinstance(obj, datetime.date):
        return date(obj)
    # Convert datetime objects with Django's time filter
    elif isinstance(obj, datetime.datetime):
        return time(obj)
    # Use ``repr()`` as the fallback serializer for unserializable objects
    else:
        return repr(obj)


@register.filter
def jsonify(obj):
    return mark_safe(json.dumps(obj, default=to_string_for_json))
