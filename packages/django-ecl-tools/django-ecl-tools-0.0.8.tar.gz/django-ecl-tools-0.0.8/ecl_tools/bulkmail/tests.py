import json
import unittest
from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.http import Http404
from bulkmail.models import Optin, List, Subscription

from django.core.exceptions import ObjectDoesNotExist
from django.test.client import Client, RequestFactory
from django.utils import unittest
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from bulkmail.views import signup, signup_verify, track


TEST_EMAIL = 'westhomas+ulrtest%s@edgecaselabs.com'

def log(p1=None, join='%s '):
    msg = ''
    for item in p1:
        msg += join % item

    return msg

class BaseTestCase(unittest.TestCase):


    def setUp(self):
        self.ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec congue faucibus diam, at pharetra eros pharetra eu. Quisque tristique turpis sed orci pulvinar lacinia. Phasellus sed ante sit amet eros pharetra mollis vel non purus. Pellentesque euismod ante ut erat tempor sit amet suscipit libero rutrum. Integer sed nulla lorem, pulvinar consequat arcu. Nulla turpis est, auctor eu adipiscing ut, pulvinar ac diam. Praesent scelerisque diam nec nibh blandit id porttitor enim sagittis. Vestibulum faucibus felis risus. Praesent vel lectus tortor, sit amet dapibus nunc."
        self.client = Client(HTTP_HOST = "django.testserver", enforce_csrf_checks=True)


class BulkmailTestCase(BaseTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()

        settings.BULKMAIL_TEST_MODE = True

        self.list = List.objects.create(sorder=0, name='newsletters', from_name="Bob's bulkmail", reply_to="no-reply@edgecaselabs.com", \
                            mail_domain='sandbox30297f221d224e7c8c39ba9cf2b77bf6.mailgun.org', address='123 any',short_description='blah',\
                            frequency='weekly',description='awesome mails')

    def testSubscribeAndOptinProcess(self):

        #Number of test accounts to create?
        accounts = 4

        rf = RequestFactory()

        #Subscribe

        #create 4 test accounts
        for i in range(1, accounts + 1):
            url = '/bm/signup'
            data = {
                'tracking': 'signup',
                'email': TEST_EMAIL % i,
                'list%s' % self.list.id: 'ON',
            }
            request = rf.post(url, data)
            response = signup(request)
            self.assertTrue(response.status_code == 200, log([url, response.status_code]))



        #Optin
        for i in range(1, accounts): #activate accounts 1-3
            email1 = Optin.objects.get(email=TEST_EMAIL % i)
            url = '/bm/signup/verify'
            data = {
                'email': TEST_EMAIL % i,
                'skey': email1.skey,
            }
            request = rf.get(url, data)
            response = signup_verify(request)
            self.assertTrue(response.status_code == 200, log([url, response.status_code]))


        #test aging optin
        i = 4
        too_old = datetime.now() - timedelta(days=10)
        email2 = Optin.objects.get(email=TEST_EMAIL % i)
        email2.created = too_old
        email2.save()

        url = '/bm/signup/verify'
        data = {
            'email': TEST_EMAIL % i,
            'skey': email2.skey,
        }
        request = rf.get(url, data)
        try:
            response = signup_verify(request)
            self.fail(log([url, response.status_code]))
        except Http404: #we expect a 404
            pass


        email2.created = datetime.now()
        email2.save()

        response = signup_verify(request)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))


        #Preview

        #Send

        #Open
        i = 1
        url = '/bm/track/' + settings.BULKMAIL_KEY
        s = 'city=San+Francisco&domain=mg.edgecaselabs.com&device-type=desktop&my_var_1=Mailgun+Variable+%231&country=US&region=CA&client-name=Chrome&user-agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%29+AppleWebKit%2F537.31+%28KHTML%2C+like+Gecko%29+Chrome%2F26.0.1410.43+Safari%2F537.31&client-os=Linux&my-var-2=awesome&ip=50.56.129.169&client-type=browser&timestamp=1406234038&token=e17a8d6590e7e8e6d81a040ec6c2507517a84c3e5aa836588d&signature=17186877f86dbbf5ae0ae357d8e7911e16958903b25c344fb0b9e807ed125ad5&body-plain='
        s += '&event=opened&list_id=%s&recipient=%s' % (self.list.id, TEST_EMAIL % i)
        data = {}
        for n in s.split('&'): data.update({n.split('=')[0]:n.split('=')[1]})

        request = rf.post(url, data)
        response = track(request, settings.BULKMAIL_KEY)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))

        self.assertTrue(response.content == 'OK', log([url, response.status_code]))

        #Click
        #NOTE: not yet supporting this

        #Unsubscribe
        i = 2
        url = '/bm/track/' + settings.BULKMAIL_KEY
        data = {
            'recipient': TEST_EMAIL % i,
            'list_id': self.list.id,
            'event': 'unsubscribed',
        }
        s = 'timestamp=1406234038&token=e17a8d6590e7e8e6d81a040ec6c2507517a84c3e5aa836588d&signature=17186877f86dbbf5ae0ae357d8e7911e16958903b25c344fb0b9e807ed125ad5&body-plain='
        for n in s.split('&'): data.update({n.split('=')[0]:n.split('=')[1]})

        request = rf.post(url, data)
        response = track(request, settings.BULKMAIL_KEY)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))

        data = json.loads(response.content)
        self.assertTrue('url' in data, log([url, response.status_code]))
        self.assertTrue('unsubscribe/success' in data['url'], log([url, response.status_code]))



        #Bounce
        i = 3
        #valid request, but no unsubscribe yet
        url = '/bm/track/' + settings.BULKMAIL_KEY
        data = {
            'recipient': TEST_EMAIL % i,
            'list_id': self.list.id,
            'event': 'bounced',
        }
        s = 'timestamp=1406234038&token=e17a8d6590e7e8e6d81a040ec6c2507517a84c3e5aa836588d&signature=17186877f86dbbf5ae0ae357d8e7911e16958903b25c344fb0b9e807ed125ad5&body-plain='
        for n in s.split('&'): data.update({n.split('=')[0]:n.split('=')[1]})
        request = rf.post(url, data)
        response = track(request, settings.BULKMAIL_KEY)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))
        self.assertTrue(response.content == 'OK', log([url, response.status_code]))
        sub = Subscription.objects.get(email=TEST_EMAIL % i)
        self.assertTrue(sub.bounce1 != None, log([url, response.status_code]))
        self.assertTrue(sub.unsubscribed == None, log([url, response.status_code]))

        #valid request, should be unsubscribed
        request = rf.post(url, data)
        response = track(request, settings.BULKMAIL_KEY)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))
        self.assertTrue(response.content == 'OK', log([url, response.status_code]))
        sub = Subscription.objects.get(email=TEST_EMAIL % i)
        self.assertTrue(sub.bounce2 != None, log([url, response.status_code]))
        self.assertTrue(sub.unsubscribed != None, log([url, response.status_code]))

        #Complaint
        #valid request, should be unsubscribed
        i = 4
        url = '/bm/track/' + settings.BULKMAIL_KEY
        data = {
            'recipient': TEST_EMAIL % i,
            'list_id': self.list.id,
            'event': 'complained',
        }
        s = 'timestamp=1406234038&token=e17a8d6590e7e8e6d81a040ec6c2507517a84c3e5aa836588d&signature=17186877f86dbbf5ae0ae357d8e7911e16958903b25c344fb0b9e807ed125ad5&body-plain='
        for n in s.split('&'): data.update({n.split('=')[0]:n.split('=')[1]})
        request = rf.post(url, data)
        response = track(request, settings.BULKMAIL_KEY)
        self.assertTrue(response.status_code == 200, log([url, response.status_code]))
        self.assertTrue(response.content == 'OK', log([url, response.status_code]))
        sub = Subscription.objects.get(email=TEST_EMAIL % i)
        self.assertTrue(sub.complaint != None, log([url, response.status_code]))
        self.assertTrue(sub.unsubscribed != None, log([url, response.status_code]))


        #Stats

        for i in range(1, accounts + 1):
            Subscription.objects.filter(email=TEST_EMAIL % i).delete()
            Optin.objects.filter(email=TEST_EMAIL % i).delete()

        self.list.delete()