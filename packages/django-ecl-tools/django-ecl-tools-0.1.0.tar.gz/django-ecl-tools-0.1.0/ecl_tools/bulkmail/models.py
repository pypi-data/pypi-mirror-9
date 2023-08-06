import base64
import random
import hashlib
from datetime import datetime
from django.core.urlresolvers import reverse

from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import importlib


imp = importlib.import_module(getattr(settings, "EMAILER", 'ecl_tools.bulkmail.mailers.mailgun'))
EMailer = imp.EMailer


class BaseEmail(object):
    html_template_name = 'email_template_sample.html'
    text_template_name = 'email_template_sample.txt'

    def get_subject(self):
        raise Exception(
            "Method 'get_subject' not created for class '%s'. Please add it to class." % self.__class__.__name__)

class BaseBulkmail(BaseEmail):

    def get_list_id(self):
        return 'list_%d' % (
            self.destination_list.id)


class List(models.Model):
    name = models.CharField(max_length=70)
    from_name = models.CharField(max_length=70)
    reply_to = models.EmailField('Reply to Address')
    mail_domain = models.CharField(max_length=70)

    address = models.TextField(help_text="Include physical address and phone number for complaints.")
    short_description = models.CharField(max_length=70)
    frequency = models.CharField(max_length=70)
    description = models.TextField()

    sorder = models.IntegerField('Order')

    def Subscribed(self):
        return Subscription.subscribed.filter(bulk_list=self).count()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('sorder',)


class SubscribedManager(models.Manager):
    def get_query_set(self):
        return super(SubscribedManager, self).get_query_set().filter(unsubscribed__isnull=True)


REASONS = (
    ('bounce', 'Bounced'),
    ('complaint', 'Complaint'),
    ('dead-address', 'Dead Address'),
    ('no-opens', 'No Activity'),
    ('bad-email', 'Bad Email'),
)

EMAIL_STATUS = (
    ('clean', 'Clean'),
    ('trap', 'Spam Trap'),
    ('invalid', 'Invalid'),
    ('bounce', 'Bounce'),
    ('suspicious', 'Suspicious'),
    ('processing', 'Processing'),
    ('no-process', 'Not Processed'),
)


class Subscription(models.Model):
    bulk_list = models.ForeignKey(List)
    email = models.EmailField()
    email_status = models.CharField(max_length=255, blank=True, null=True, default='no-process', choices=EMAIL_STATUS)
    is_clean = models.BooleanField(default=False)
    signup_location = models.CharField(max_length=300, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    # opens = models.IntegerField(default=0, blank=True)
    #last_open = models.DateTimeField(blank=True, null=True)

    bounce1 = models.DateTimeField(blank=True, null=True)
    bounce2 = models.DateTimeField(blank=True, null=True)
    complaint = models.DateTimeField(blank=True, null=True)

    unsubscribed = models.DateTimeField(blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True, choices=REASONS)

    objects = models.Manager()
    subscribed = SubscribedManager()

    def __unicode__(self):
        return self.email


class Optin(BaseBulkmail, models.Model):
    def __init__(self, *args, **kwargs):
        super(Optin, self).__init__(*args, **kwargs)

        self.html_template_name = "email_optin.html"
        self.text_template_name = "email_optin.txt"


    email = models.EmailField()
    skey = models.CharField(max_length=255)
    signup_location = models.CharField(max_length=300, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    bulk_lists = models.ManyToManyField(List)


    def __unicode__(self):
        return self.email

    def render(self, preview=False, format='html', test=False, context=None):

        if not context:
            context = {}
        context.update({'optin': self, 'MEDIA_URL': settings.MEDIA_URL})

        if format == 'txt':
            return render_to_string(self.text_template_name, context)

        return render_to_string(self.html_template_name, context)

    def send_email(self, host):
        c = {'host': host,}
        text = self.render(format='txt', context=c)
        html = self.render(context=c)

        emailer = EMailer(
            settings.DEFAULT_FROM_MAIL_DOMAIN
        )

        context = {
            'to': [self.email],
            'subject': 'Please verify your e-mail',
            'from': settings.DEFAULT_FROM_EMAIL,
            # 'reply_to': settings.DEFAULT_FROM_EMAIL,
            #'mail_domain': settings.DEFAULT_FROM_MAIL_DOMAIN,
            'html': html,
            'text': text,
        }

        emailer.send(context)

        emailer.close()

        self.sent = datetime.now()
        self.save()

    @staticmethod
    def generate_optin_key():
        while 1:
            skey = base64.b64encode(hashlib.sha224(str(random.getrandbits(256))).digest(),
                                    random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')
            if Optin.objects.filter(skey=skey).count() == 0:
                break

        return skey


class Campaign(models.Model):
    subject = models.CharField(max_length=255)
    bulk_list = models.ForeignKey(List)

    html = models.TextField()
    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    sent = models.DateTimeField(blank=True, null=True)
    scheduled = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ('-created',)


EVENT_TYPES = (
    ('opened', 'opened'),
    ('clicked', 'clicked'),
    ('unsubscribed', 'unsubscribed'),
    ('complained', 'complained'),
    ('bounced', 'bounced'),
    ('dropped', 'dropped'),
    ('delivered', 'delivered'),
)


class TrackingEvent(models.Model):
    subscription = models.ForeignKey(Subscription)
    campaign = models.CharField(max_length=50)
    event = models.CharField(max_length=12, choices=EVENT_TYPES)
    client_os = models.CharField(max_length=50, null=True, blank=True)
    client_name = models.CharField(max_length=50, null=True, blank=True)
    client_type = models.CharField(max_length=50, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=10, null=True, blank=True)
    ip = models.CharField(max_length=15, null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)

class BaseBulkmailModel(BaseBulkmail, models.Model):
    sent = models.DateTimeField('Sent/Published', blank=True, null=True)
    scheduled = models.DateTimeField('Scheduled Send On', blank=True, null=True)
    # expires = models.DateTimeField('Site Display Expire')
    destination_list = models.ForeignKey(List, blank=True, null=True,
                                         help_text="IMPORTANT: The list where you will be sending this email campaign.")
    created = models.DateTimeField(auto_now_add=True)

    def get_campaign_id(self):
        return 'email_%d' % (
            self.id)

    @property
    def utm_source(self):
        raise Exception("You must define the utm_source property in your inherited class.")


    # def stats(self):
    #     if self.sent:
    #         return '<a href="%s://%s/api/stats/%s/%s/" target="_blank">View Stats</a>' % (
    #             protocol,
    #             settings.BMAIL_HOST,
    #             self.get_list_id(),
    #             self.get_campaign_id(),
    #         )
    #
    #     return ''
    #
    # Stats.allow_tags = True

    def preview(self, ):
        return '<a href="%s">Preview and Send</a>' % (reverse('bulkmail_preview', args=[self.id]))
    

    preview.allow_tags = True
    


    def render(self, preview=False, format='html', test=False, context=None):

        c = {
            'obj': self,
            'preview': preview,
            'test': test,
            'list': self.destination_list,
            'unsubscribe': '{{ unsubscribe }}',
            'email_tag': '<!--{{ email }}-->',
            'analytics': self.analytics,
        }
        if context:
            c.update(context)

        if format == 'txt':
            return render_to_string(self.text_template_name, c)

        return render_to_string(self.html_template_name, c)


    @property
    def analytics(self):
        return 'utm_source=%s&utm_medium=email&utm_campaign=%s' % (self.utm_source, self.get_campaign_id())

    def send_bulkmail(self, emails=None):

        test = True if emails else False

        if not self.sent or test:

            html = self.render(test=test)
            text = self.render(test=test, format='txt')

            subject = unicode(self.get_subject())
            subject = subject.replace('{star}', u'\u2605').replace('*', u'\u2605')

            emailer = EMailer(
                self.destination_list.mail_domain
            )

            list_id = self.get_list_id()
            campaign = self.get_campaign_id()

            if not test:
                subs = Subscription.objects.filter(unsubscribed__isnull=True,
                                                   bulk_list=self.destination_list).distinct(
                    'email')

                recipient_variables = {}
                for sub in subs:
                    recipient_variables.update({sub.email: {'id': sub.id}})
            else:
                if not isinstance(emails, list):
                    emails = [emails]

                recipient_variables = {}
                for i in range(0, len(emails)):
                    recipient_variables.update({emails[i]: {'id': 'test%s' % i}})

                list_id += '-test'

            context = {
                'recipient-variables': recipient_variables,
                'subject': subject,
                'from': '%s <%s>' % (self.destination_list.from_name, self.destination_list.reply_to),
                'v:list': list_id,
                'v:campaign': campaign,
                'html': html,
                'text': text,
            }

            emailer.send(context)

            emailer.close()

            if not test:
                self.sent = datetime.now()
                self.save()

            print '%s %s send_bulkmail completed.' % (self.__class__.__name__, self.id)

    def is_published(self):
        if self.scheduled is not None:
            if ( self.expires > datetime.now() ):
                return True

        return False

    def is_expired(self):
        now = datetime.now()
        if now > self.expires:
            return True

        return False


    def __unicode__(self):
        return self.get_subject()

    class Meta:
        abstract = True
        ordering = ('-sent',)