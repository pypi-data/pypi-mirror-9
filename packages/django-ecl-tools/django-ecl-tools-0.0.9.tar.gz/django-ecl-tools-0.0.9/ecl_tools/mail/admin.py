from django.db import models
from django.contrib import admin
from models import *


class MailMessageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('from_email', 'recipient_list', 'subject', 'message', 'status', 'status_details',)
        }),
    )
    list_display	= ('from_email', 'recipient_list', 'subject', 'status_text', 'status_details', 'created', 'modified',)

class SMSMessageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('from_phone', 'to', 'message', 'status', 'status_details',)
        }),
    )
    list_display	= ('from_phone', 'to', 'status_text', 'status_details', 'created', 'modified',)

admin.site.register(MailMessage, MailMessageAdmin)
admin.site.register(SMSMessage, SMSMessageAdmin)
