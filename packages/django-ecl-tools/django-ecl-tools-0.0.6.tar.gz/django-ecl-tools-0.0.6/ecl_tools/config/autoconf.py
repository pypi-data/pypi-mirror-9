from django.conf import settings
from models import *

def check_defaults():
    """
    Check for and load the default configs for a Site.
    """

    GLOBAL_CONFIG_DEFAULTS = getattr(settings, "GLOBAL_CONFIG_DEFAULTS", {})

    object_list = GlobalConfig.objects.all()
    if len(GLOBAL_CONFIG_DEFAULTS) != len(object_list):
        for key, val in GLOBAL_CONFIG_DEFAULTS.items():
            if not GlobalConfig.objects.filter(field__exact=key):
                new_field = GlobalConfig()
                new_field.field = key
                new_field.value = val
                new_field.save()


    CONFIG = getattr(settings, "EMAIL_TEMPLATE_DEFAULTS", {})

    object_list = EmailTemplate.objects.all()
    if len(CONFIG) != len(object_list):
        for key, val in CONFIG.items():
            if not EmailTemplate.objects.filter(name__exact=key):
                new_field = EmailTemplate()
                new_field.name = key
                new_field.subject = val['subject']
                new_field.body = val['body']
                new_field.save()

