from django.db import models
from django.contrib import admin
from models import *

class GlobalConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('field', 'value',)
        }),
        )
    list_display	= ('field', 'value_trimmed', 'created', 'modified',)

    def value_trimmed(self, obj):
        return "%s.." % obj.value[:75] if len(obj.value) > 75 else obj.value
    value_trimmed.short_description = 'Value'

admin.site.register(GlobalConfig, GlobalConfigAdmin)



class EmailTemplateAdmin(admin.ModelAdmin):
    pass

admin.site.register(EmailTemplate, EmailTemplateAdmin)

