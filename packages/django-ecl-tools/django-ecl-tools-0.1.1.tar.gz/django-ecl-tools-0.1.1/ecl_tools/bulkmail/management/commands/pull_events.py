from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

from bulkmail.models import TrackingEvent, Subscription
from newsletters.models import Newsletter


class Command(BaseCommand):
    args = '<newsletter id>'
    help = '!!!THIS IS DESTRUCTIVE!!! Used to pull down data from MailGun that may have missed the webhooks.'

    def handle(self, *args, **options):

        n = Newsletter.objects.get(id=args[0])

        campaign = n.get_campaign_id()

        #remove all existing tracking events
        #TrackingEvent.objects.filter(campaign=campaign).update(campaign=campaign+'_old')

        import requests, json
        url = "https://api.mailgun.net/v2/%s/events" % n.destination_list.mail_domain
        key = settings.MAILGUN_API_KEY

        params={
            #"event": "delivered OR opened OR clicked OR failed OR complained OR unsubscribed OR dropped",
            #"subject": n.title,
            #"event": "failed",
            "pretty": "yes"
        }

        while True:
            r = requests.get(url, auth=("api", key), params=params)
            d = json.loads(r.content)

            #work with data
            if len(d['items']) == 0:
                print "No items found for query."
                print 'All done!!!!'
                return 0

            for item in d['items']:

                user_vars = item.get('user-variables')
                if not user_vars:
                    continue

                user_campaign = user_vars['campaign']
                if user_campaign == campaign: #only data that matches campaign

                    recipient = item.get('recipient')

                    if not recipient:
                        continue

                    list_id = user_vars.get('list').replace('list_', '')
                    if not list_id or '-test' in list_id:
                        continue

                    subs = Subscription.objects.filter(email__iexact=recipient, bulk_list_id=int(list_id))
                    if not subs:
                        continue
                    sub = subs[0]

                    time = datetime(1970,1,1) + timedelta(seconds=item.get('timestamp'))

                    event = item['event']

                    try:
                        if event == 'failed':
                            if item.get('reason') == 'bounce':
                                event = 'bounced'

                        e = TrackingEvent.objects.get(campaign=campaign, event=event, subscription=sub)
                        e.time = time
                        e.save()

                        if event == 'unsubscribed':
                            sub.unsubscribed = time
                            sub.save()

                        elif event == 'complained' or event == 'bounced':

                            if event == 'complained':
                                sub.complaint = time
                                sub.unsubscribed = time
                                sub.reason = 'complaint'
                            else:
                                if sub.bounce1:
                                    sub.bounce2 = time
                                    sub.unsubscribed = time
                                    sub.reason = 'bounce'
                                else:
                                    sub.bounce1 = time
                            sub.save()


                        print '.'
                    except TrackingEvent.MultipleObjectsReturned:
                        print 'More than one return for %s %s %s' % (campaign, event, sub)
                        e = TrackingEvent.objects.filter(campaign=campaign, event=event, subscription=sub, time__isnull=True)
                        if e:
                            e = e[0]
                            e.time = time
                            e.save()
                            print('Updated first occurrence')
                        else:
                            print 'No matching events are missing timestamp. Skipping this one.'
                    except TrackingEvent.DoesNotExist:
                        print 'No records found for %s %s %s' % (campaign, event, sub)
                        geolocation = item.get('geolocation')
                        client_info = item.get('client-info')
                        extra_data = {
                            'campaign': campaign,
                            'event': event,
                            'subscription': sub,
                            'ip': item.get('ip'),
                            'country': geolocation.get('country') if geolocation else None,
                            'region': geolocation.get('region') if geolocation else None,
                            'city': geolocation.get('city') if geolocation else None,
                            'user_agent': client_info.get('user-agent') if client_info else None,
                            'device_type': client_info.get('device-type') if client_info else None,
                            'client_type': client_info.get('client-type') if client_info else None,
                            'client_name': client_info.get('client-name') if client_info else None,
                            'client_os': item.get('client-os') if client_info else None,
                            'time': time,
                        }
                        #log the event
                        TrackingEvent.objects.create(**extra_data)
                        print 'Record created.'




            #decision if we continue
            if 'next' in d['paging']:
                if url != d['paging']['next']: #MG ALWAYS puts a next page; even when there are no other pages; so check if the URL is the same as the last time.
                    url = d['paging']['next']
                    print 'Next page...'
                    continue