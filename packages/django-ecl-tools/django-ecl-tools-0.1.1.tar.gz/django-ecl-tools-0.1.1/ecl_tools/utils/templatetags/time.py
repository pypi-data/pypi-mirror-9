from datetime import datetime
from django.conf import settings
from django.template import Library

register = Library()



@register.filter
def ordinal(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return "%s%s" % (day, suffix)


@register.filter
def ago(value):
    if not value:
        return ""
    n = None
    if settings.TIME_ZONE:
        try:
            import pytz
            n = datetime.now(tz=pytz.timezone(str(settings.TIME_ZONE)))
        except:
            pass
    if not n:
        #fall back to non-timezone now()
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