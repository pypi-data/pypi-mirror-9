from django.template import Library

from ecl_tools.config.models import GlobalConfig

register = Library()

@register.simple_tag
def global_config(key, default=""):
        return GlobalConfig.get_or_none(key, default=default)
