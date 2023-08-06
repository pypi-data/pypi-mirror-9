from django.conf.urls import *

urlpatterns = patterns('ecl_tools.bulkmail.views',
   
   url(r'^signup$', 'signup', name="bulkmail_signup"),
   url(r'^signup/verify$', 'signup_verify', name="bulkmail_signup_verify"),
   url(r'^unsubscribe/success$', 'unsubscribe_success',
       name="bulkmail_unsubscribe_success"),

   url(r'^track/(?P<key>.+)', 'track', name="bulkmail_track"),
   url(r'^stats/(?P<key>.+)', 'stats', name="bulkmail_stats"),
)