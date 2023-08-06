from django.template import Library



register = Library()



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
