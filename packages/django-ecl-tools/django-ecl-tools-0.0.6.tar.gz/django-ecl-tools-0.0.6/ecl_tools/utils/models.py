import datetime
from django.conf import settings
from django.contrib import admin 
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

#from managers import MultiHostSiteManager


STATUS_CHOICES = (
    (1, _('draft')),
    (2, _('active')),
    (3, _('done')),
)

class BaseModel(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    #NOTE: dynamic related name for abstract class. see https://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    #site = models.ForeignKey(Site, null=True, blank=False, related_name='%(app_label)s_%(class)s_related',)

    objects = models.Manager()
    #on_site = MultiHostSiteManager()

    # def get_site_label(self):
    #     try:
    #         return self.site
    #     except Site.DoesNotExist:
    #         return  '???'

    class Meta:
        abstract = True


class BaseContent(BaseModel):
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)#, unique=True)
    content = models.TextField(_('content'), blank=True, null=True)
    #NOTE: dynamic related name for abstract class. see https://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    author = models.ForeignKey(User, blank=False, null=True, related_name='%(app_label)s_%(class)s_related',)
    status = models.IntegerField(_('status'), max_length=1, choices=STATUS_CHOICES, default=2)
    published = models.DateField(_('published'), blank=True, null=True)

    def __unicode__ (self):
        return "%s [Created %s]" % (self.slug, str(self.created.strftime("%x %X")))

    def clean(self):
        if self.status == 1 and self.published is not None:
            raise ValidationError("Draft entries cannot have a publication date.")
        elif self.status > 1 and self.published is None:
            self.published = datetime.datetime.now()

    def mark_as_done(self):
        self.status = 3

    @property
    def status_text(self):
        return STATUS_CHOICES[self.status-1][1].encode('utf-8')

    @property
    def is_draft(self):
        return self.status == 1
    @property
    def is_published(self):
        return self.status == 2
    @property
    def is_done(self):
        return self.status == 3

    class Meta:
        abstract = True

