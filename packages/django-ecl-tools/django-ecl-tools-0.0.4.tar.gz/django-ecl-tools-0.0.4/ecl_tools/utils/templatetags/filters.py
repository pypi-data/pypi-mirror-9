from datetime import datetime, date
import re
import itertools
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Library

register = Library()

@register.filter
def currency(dollars):
    if not dollars:
        return ""
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

@register.filter("round")
def round_value(value):
    if not value:
        return ""
    return round(value)

@register.filter
def times(value, arg):
    if not value:
        return ""
    return value * arg


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
def age(value):
    if value:
        n = datetime.now()
        d = n - value
        months = d.days / 31
        years = d.days / 365
        if years > 0:
            return "%s yrs" % years
        else:
            return "%s mths" % months
    else:
        return ""

@register.filter
def relativetime(value):
    if not value:
        return ""

    n = datetime.now()
    d = n - value
    secs = d.total_seconds()
    #mins
    time = [round(secs / 60), "min"]
    if time[0] > 60:
        #hours
        time = [round(time[0] / 60), "hour"]
        if time[0] > 24:
            #days
            time = [round(time[0] / 24), "day"]
            if time[0] > 31:
                #months
                time = [round(time[0] / 31), "mth"]
                if time[0] > 12:
                    #years
                    time = [round(time[0] / 12), "yr"]
    return "%s %s%s" % (int(time[0]), time[1], "" if time[0] == 1 else "s")



@register.filter
def to_class_name(value):
    return value.__class__.__name__

@register.filter
def format_datetime(value, format='Y-m-d'):
    """
    Monday, December 1, 2021
    l, F j, Y
    https://docs.djangoproject.com/en/1.1/ref/templates/builtins/#now
    """
    if value:
        from django.template.defaultfilters import date as django_date_filter
        return django_date_filter(value, format)
    else:
        return None

@register.filter
def dateToName(value):
    diff = (date.today() - value).days
    if diff == 0:
        return 'TODAY'
    elif diff == -1:
        return 'TOMORROW'
    else:
        return 'THE NEXT DAY'

@register.filter("format")
def format_string(value, *args, **kwargs):
    try:
        s = value.format(*args, **kwargs)
        return s
    except TypeError, e:
        return ''

@register.filter
def markdown(value):
    """
    Run string through markdown library processor and return HTML.
    """
    if value:

        value = stripcomments(value)

        import markdown
        return Markup(markdown.markdown(value))
    else:
        return ""

def stripcomments(value):
    """
    Remove HTML comments from string.
    """
    if value:
        #remove comments
        value = re.sub('<!--.*?-->', '', value, flags=re.DOTALL)
        #remove weird XML crap
        value = re.sub('<\?.*?>', '', value, flags=re.DOTALL)

    return value

register.filter('stripcomments', stripcomments)



def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        else:
            return fn(field, attr)
    return wrapped


def _process_field_attributes(field, attr, process):

    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    if len(params) != 2:
        raise ValueError('Invalid format for adding an HTML attribute to %s; use the following format: attribute_name:attribute value' % field)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        return old_as_widget(widget, attrs, only_initial)

    bound_method = type(old_as_widget)
    try:
        field.as_widget = bound_method(as_widget, field, field.__class__)
    except TypeError: # python 3
        field.as_widget = bound_method(as_widget, field)
    return field


def process(widget, attrs, attribute, value):
    attrs[attribute] = value


@register.filter("attr")
@silence_without_field
def set_attr(field, attr):
    return _process_field_attributes(field, attr, process)


def process_append(widget, attrs, attribute, value):
    if attrs.get(attribute):
        attrs[attribute] += ' ' + value
    elif widget.attrs.get(attribute):
        attrs[attribute] = widget.attrs[attribute] + ' ' + value
    else:
        attrs[attribute] = value


@register.filter("append_attr")
@silence_without_field
def append_attr(field, attr):
    return _process_field_attributes(field, attr, process_append)

@register.filter("add_class")
@silence_without_field
def add_class(field, css_class):
    return _process_field_attributes(field, 'class:' + css_class, process_append)

@register.filter("add_error_class")
@silence_without_field
def add_error_class(field, css_class):
    if hasattr(field, 'errors') and field.errors:
        return add_class(field, css_class)
    return field


@register.filter("set_data")
@silence_without_field
def set_data(field, data):
    return _process_field_attributes(field, 'data-' + data, process)

