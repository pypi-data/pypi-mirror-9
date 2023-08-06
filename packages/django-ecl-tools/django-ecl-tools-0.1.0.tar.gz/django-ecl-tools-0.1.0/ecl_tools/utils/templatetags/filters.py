import re
import itertools
from datetime import datetime, date

from django.template import Library


register = Library()


@register.filter
def split(value, arg):
    """
    Usage: {{ "string"|split("/") }}
    """
    return value.split(arg)

@register.filter
def add_where(value, attr_equals):
    count = 0
    attr, equals = attr_equals.split(':')
    for item in value:
        obj = item
        for prop in attr.split('.'):
            obj = getattr(obj, prop)
        if str(obj) == equals:
            count = count + 1

    return count

@register.filter
def chain(value, arg):
    return itertools.chain(value, arg)

@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter("format")
def format_string(value, *args, **kwargs):
    try:
        s = value.format(*args, **kwargs)
        return s
    except TypeError, e:
        return ''

