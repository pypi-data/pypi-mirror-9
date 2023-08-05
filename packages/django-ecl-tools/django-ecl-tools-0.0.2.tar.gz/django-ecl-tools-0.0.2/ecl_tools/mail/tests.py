from django.core.exceptions import ObjectDoesNotExist
from django.test.client import Client
from django.utils import unittest
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from ecl_tools.tests import BaseTestCase, log
from ecl_tools.mail.models import MailMessage
from ecl_tools.mail.core import send_mail

class MailTestCase(BaseTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

    def test_mail_queue(self):

        subject = 'test subject'
        message = 'test message'
        sender = 'test@email.com'
        to = 'test_to@email.com'

        send_mail(subject, message, sender, to)

        self.assertEquals(MailMessage.objects.all().count(), 1)

        msg = MailMessage.objects.all()[0]

        self.assertEquals(1, msg.status)
        self.assertEquals(subject, msg.subject)
        self.assertEquals(message, msg.message)
        self.assertEquals(sender, msg.from_email)
        self.assertEquals(to, msg.recipient_list)

