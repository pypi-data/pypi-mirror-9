import re
import csv

from django import forms
from django.core.management.base import BaseCommand

from bulkmail.models import List, Subscription


class Command(BaseCommand):
    args = '<list id> <signup location> <start> <end> <csv csv ...>'
    help = 'Import e-mails directly into list.'

    def handle(self, *args, **options):
        bulklist = List.objects.get(id=args[0])

        # if len(args) > 2:
        signup_location = args[1]
        slice_start = int(args[2])
        slice_end = int(args[3])
        paths = args[4:]

        #else:
        #  paths = args[1:]

        print 'Importing %s' % bulklist.name
        for path in paths:
            email_col = 0
            subs = []

            with open(path, 'rU') as fh:
                reader = csv.reader(fh.read().splitlines())
                for i, row in enumerate(reader):

                    if i == 0:
                        for j, r in enumerate(row):
                            if re.search("email", r, re.I) or re.search("e-mail", r, re.I):
                                email_col = j
                                break

                    else:

                        if i - 1 >= slice_start and i - 1 < slice_end:
                            f = forms.EmailField()

                            try:
                                email = f.clean(row[email_col])

                            except:
                                pass

                            else:
                                subs.append(
                                    Subscription(email=email, signup_location=signup_location, bulk_list=bulklist))

            Subscription.objects.bulk_create(subs)
      