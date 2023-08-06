import re
from django.utils import unittest
from django.conf import settings
from django.utils.html import escape
from re_venue.tests import BaseReVenueTestCase, log
from django.contrib.auth.models import User
from re_venue.config.models import Config

from re_venue.conf import request_settings

class ConfigTestCase(BaseReVenueTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()


    def test_configs(self):

        #response = self.client.post('/admin/login', {'username': 'test_user', 'password': 'tester12'})
        #self.assertTrue(response.status_code == 200)


        url = '/admin/config'
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))
        self.assertRegexpMatches(response.content, '<h1>Site Config</h1>')


        configs = Config.on_site.all()
        for config in configs:
            self.assertRegexpMatches(response.content, config.field)

        for config in configs:
            url = '/admin/config/edit/%s' % (config.id)
            response = self.client.get(url)
            self.assertTrue(response.status_code == 200, log([url, response.status_code]))
            self.assertRegexpMatches(response.content, config.field)
            self.assertRegexpMatches(response.content, re.escape(escape(config.value)))


