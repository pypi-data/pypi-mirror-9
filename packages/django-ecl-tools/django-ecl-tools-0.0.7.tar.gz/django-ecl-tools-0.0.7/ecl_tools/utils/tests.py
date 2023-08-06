from django.core.exceptions import ObjectDoesNotExist
from django.test.client import Client
from django.utils import unittest
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

def log(p1=None, join='%s '):
    msg = ''
    for item in p1:
        msg += join % item

    return msg

class BaseTestCase(unittest.TestCase):
    #fixtures = ['config.json',]

#    @classmethod
#    def setUpClass(cls):
#        super(BaseReVenueTestCase, cls).setUpClass()
#
#    @classmethod
#    def tearDownClass(cls):
#        super(BaseReVenueTestCase, cls).tearDownClass()


    def setUp(self):
        self.ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec congue faucibus diam, at pharetra eros pharetra eu. Quisque tristique turpis sed orci pulvinar lacinia. Phasellus sed ante sit amet eros pharetra mollis vel non purus. Pellentesque euismod ante ut erat tempor sit amet suscipit libero rutrum. Integer sed nulla lorem, pulvinar consequat arcu. Nulla turpis est, auctor eu adipiscing ut, pulvinar ac diam. Praesent scelerisque diam nec nibh blandit id porttitor enim sagittis. Vestibulum faucibus felis risus. Praesent vel lectus tortor, sit amet dapibus nunc."
        self.client = Client(HTTP_HOST = "django.testserver")

        #make any web request to init db with site
        self.client.get('/')
        site = Site.objects.all()[0]
        self.site_id = site.id
        settings.SITE_ID = self.site_id

        self.user_username = 'test_user'
        self.user_email = 'test@test.com'
        self.user_password = 'tester12'
        try:
            self.user = User.objects.get(username=self.user_username)
            self.is_first_run = False
        except ObjectDoesNotExist:
            self.user = User.objects.create_superuser(self.user_username, self.user_email, self.user_password)
            self.is_first_run = True

        self.client.login(username=self.user_username, password=self.user_password)
        if self.is_first_run:
            self.client.get('/?autoconf=1') #init the basic server setup


    def tearDown(self):
        self.client.logout()

