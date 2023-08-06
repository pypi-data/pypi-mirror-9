from django.core.management.base import BaseCommand

from bulkmail.models import Subscription, List


class Command(BaseCommand):
    def handle(self, *args, **options):

        remove = True if len(args) > 0 and args[0] == 'remove' else False


        for list in List.objects.all():
            unique_emails = []
            subs = Subscription.objects.filter(bulk_list=list)
            for s in subs:
                if not s.email.lower() in unique_emails:
                    unique_emails += [s.email.lower()]

            print "%s unique emails of %s total in list %s" % (len(unique_emails), subs.count(), list)

            if len(unique_emails) != subs.count(): #mismatch! do a detailed search
                dup_emails = []
                for email in unique_emails:
                    subs = Subscription.objects.filter(bulk_list=list, email__iexact=email)
                    if subs.count() > 1:
                        print "%s dups found for %s" % (len(subs[1:]), email)
                        dup_emails += [s.email for s in subs[1:]]

                print "%s dup emails in list %s" % (len(dup_emails), list)
                print dup_emails

                if remove:
                    for dup in dup_emails:
                        s = Subscription.objects.get(bulk_list=list, email=dup)
                        print 'Removing %s dup' % s
                        s.delete()
