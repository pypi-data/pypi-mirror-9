from django.db import models
from django.utils.translation import ugettext_lazy as _

class GlobalConfig(models.Model):
    """
    Application configs.
    """
    field = models.CharField(_('field'), max_length=50)
    value = models.CharField(_('value'), max_length=500)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    @staticmethod
    def get_or_none(field, default=None):
        try:
            return GlobalConfig.objects.get(field=field).value
        except GlobalConfig.DoesNotExist:
            return default

    def __unicode__ (self):
        return "%s (::global::) [Created %s]" % (self.field, str(self.created.strftime("%x %X")))

class EmailTemplate(models.Model):

    name = models.CharField(max_length=50)

    subject = models.CharField(max_length=78)
    body = models.TextField(null=True)


    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.name, self.created)

    def get_body(self, **kwargs):

        from string import Template
        return Template(self.body).safe_substitute(**kwargs)

