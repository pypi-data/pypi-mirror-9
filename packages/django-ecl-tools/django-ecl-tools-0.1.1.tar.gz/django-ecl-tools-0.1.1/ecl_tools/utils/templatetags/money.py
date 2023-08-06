from django.template import Library
from django.contrib.humanize.templatetags.humanize import intcomma

register = Library()

@register.filter
def currency(dollars):
    if not dollars:
        return ""
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
