import json
from datetime import datetime, timedelta
import hashlib
import hmac

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from bulkmail.forms import SignupForm
from bulkmail.mailers.mailgun import RejectEventResponse
from .ecl_tools.bulkmail.models import List, Subscription, Optin, TrackingEvent
from newsletters.models import Newsletter


def verify(key, request):
    try:
        return key == settings.BULKMAIL_KEY and \
               verify_signature(settings.MAILGUN_API_KEY,
                                request.REQUEST['token'],
                                request.REQUEST['timestamp'],
                                request.REQUEST['signature'])
    except KeyError:
        return False

def verify_signature(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token),
                             digestmod=hashlib.sha256).hexdigest()



def unsubscribe_success(request):
    lid = request.GET.get('lid', '')
    blist = get_object_or_404(List, id=lid)
    return TemplateResponse(request, 'unsubscribe_success.html', {'list': blist})


@csrf_exempt
def track(request, key):

    if verify(key, request):

        event = request.REQUEST.get('event')
        list_id = request.REQUEST.get('list')
        campaign = request.REQUEST.get('campaign')
        recipient = request.REQUEST.get('recipient')

        if list_id:

            list_id = list_id.replace('list_', '')

            if '-test' in list_id:
                #skip tests
                return http.HttpResponse('OK', mimetype="text/plain")

            try:
                sub = Subscription.objects.get(email__iexact=recipient, bulk_list_id=list_id)
                time = datetime(1970,1,1) + timedelta(seconds=float(request.REQUEST.get('timestamp')))
                extra_data = {
                    'campaign': campaign,
                    'event': event,
                    'subscription': sub,
                    'ip': request.REQUEST.get('ip'),
                    'country': request.REQUEST.get('country'),
                    'region': request.REQUEST.get('region'),
                    'city': request.REQUEST.get('city'),
                    'user_agent': request.REQUEST.get('user-agent'),
                    'device_type': request.REQUEST.get('device-type'),
                    'client_type': request.REQUEST.get('client-type'),
                    'client_name': request.REQUEST.get('client-name'),
                    'client_os': request.REQUEST.get('client-os'),
                    'time': time,
                }


                #log the event
                TrackingEvent.objects.create(**extra_data)


                if event == 'unsubscribed':
                    now = datetime.now()
                    for subs in Subscription.objects.filter(email__iexact=recipient, unsubscribed__isnull=True, bulk_list_id=list_id):
                        subs.unsubscribed = now
                        subs.save()

                    url = 'http://%s%s?lid=%s' % (request.get_host(), reverse('bulkmail_unsubscribe_success'), list_id)

                    json_dump = json.dumps({'url': url})
                    return http.HttpResponse(json_dump, mimetype='application/json')

                elif event == 'complained' or event == 'bounced':

                    now = datetime.now()
                    for subs in Subscription.objects.filter(email__iexact=recipient, unsubscribed__isnull=True):
                        if event == 'complained':
                            subs.complaint = now
                            subs.unsubscribed = now
                            subs.reason = 'complaint'
                        else:
                            if subs.bounce1:
                                subs.bounce2 = now
                                subs.unsubscribed = now
                                subs.reason = 'bounce'
                            else:
                                subs.bounce1 = now
                        subs.save()


                return http.HttpResponse('OK', mimetype="text/plain")

            except Subscription.DoesNotExist:
                #bad email lookup; ignore it and reject
                pass

    return RejectEventResponse()


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        jdict = {'status': 'error', 'message': 'Invalid E-Mail Address'}
        if form.is_valid():
            jdict = {'status': 'ok'}
            tracking = form.cleaned_data['tracking']
            if tracking is None:
                tracking = 'unknown'

            optin = Optin.objects.create(email=form.cleaned_data['email'], signup_location=tracking, skey=Optin.generate_optin_key())
            for l in List.objects.all():
                value = request.POST.get('list%d' % l.id, '')
                if value == 'ON':
                    optin.bulk_lists.add(l)
                optin.save()

            optin.send_email(request.get_host())

        return http.HttpResponse(json.dumps(jdict), mimetype='application/javascript')

    raise http.Http404


def signup_verify(request):
    email = request.GET.get('email', '')
    skey = request.GET.get('skey', '')
    old = datetime.now() - timedelta(days=10)
    optin = get_object_or_404(Optin, skey=skey, email=email, created__gte=old)
    blists = []
    for l in optin.bulk_lists.all():
        if Subscription.subscribed.filter(email__iexact=optin.email, bulk_list=l).count() == 0:
            s = Subscription(email=optin.email, signup_location=optin.signup_location, bulk_list=l)
            s.save()

        blists.append(l)

    optin.delete()
    c = {'lists': blists}
    return TemplateResponse(request, 'signup_verified.html', c)


@login_required 
def stats(request, key):
    newsletter = Newsletter.objects.get(pk=key)
    c = {
        'tracking_events': newsletter.stats,
        'hello': 'hello'
    }
    return TemplateResponse(request, 'bulkmail/stats.html', c)








