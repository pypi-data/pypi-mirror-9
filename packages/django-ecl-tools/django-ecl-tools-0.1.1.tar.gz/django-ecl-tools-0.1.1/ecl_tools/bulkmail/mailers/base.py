import re
import urllib
import hashlib
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


class BaseEmailer(object):
    def __init__(self, mail_domain):
        #self.reply_to = reply_to
        #self.text_tpl = text_tpl
        #self.html_tpl = html_tpl
        #self.list_id = list_id
        #self.campaign_id = campaign_id
        self.mail_domain = mail_domain
        #self.salt = salt
        #self.analytics = analytics

        #self.text_urls = {}
        #self.html_urls = {}
        # if from_address:
        #     self.from_address = from_address
        # else:
        #     self.from_address = settings.DEFAULT_FROM_EMAIL
        # self.from_name = from_name

    # def get_from_address(self):
    #     if self.from_name:
    #         return '%s <%s>' % (self.from_name, self.from_address)
    #     else:
    #         return self.from_address


    # def headers(self, unsubscribe):
    #     h = {
    #         'List-Id': self.list_id,
    #         'List-Unsubscribe': '<%s>' % unsubscribe,
    #     }
    #     return h

    def send(self, context, log=True):
        raise NotImplementedError

