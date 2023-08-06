from datetime import date

from django.core.management.base import BaseCommand

from bulkmail.models import Subscription


class Command(BaseCommand):
    def handle(self, *args, **options):
        # args list_id, interval
        now = date.today()
        for s in Subscription.objects.raw(
                                                  "SELECT * FROM bulkmail_subscription WHERE (last_open is NULL or last_open < current_date - interval '" +
                                                  args[1] + "' day) AND (created < current_date - interval '" + args[
                                    1] + "' day) AND bulk_list_id =" + args[0] + " AND unsubscribed is NULL"):
            s.unsubscribed = now
            s.reason = 'no-opens'
            s.save()