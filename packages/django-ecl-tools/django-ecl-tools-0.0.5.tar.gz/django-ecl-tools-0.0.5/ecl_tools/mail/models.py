from django.db import models
from django.utils.translation import ugettext_lazy as _

from ecl_tools.utils.models import BaseModel

STATUS_CHOICES = (
    (1, _('active')),
    (2, _('sent')),
    (3, _('error')),
    )
class MailMessage(BaseModel):

    from_email = models.EmailField(max_length=255)
    recipient_list = models.CharField(max_length=500)
    subject = models.CharField(max_length=500)
    message = models.TextField()

    status = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=1)
    status_details = models.TextField(blank=True, null=True)


    @property
    def status_text(self):
        return STATUS_CHOICES[self.status-1][1].encode('utf-8')


    def __unicode__ (self):
        return "%s - %s [Created %s]" % (self.subject, self.status_text, str(self.created.strftime("%x %X")))


class SMSMessage(BaseModel):

    from_phone = models.CharField(max_length=10)
    to = models.CharField(max_length=10)
    message = models.TextField()

    status = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=1)
    status_details = models.TextField(blank=True, null=True)


    @property
    def status_text(self):
        return STATUS_CHOICES[self.status-1][1].encode('utf-8')


    def __unicode__ (self):
        return "%s - %s [Created %s]" % (self.to, self.status_text, str(self.created.strftime("%x %X")))
