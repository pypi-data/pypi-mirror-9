from django.core.management.base import BaseCommand, CommandError


def history(username=None, num_of_records=None):

    from django.contrib.admin.models import LogEntry

    if not num_of_records:
        num_of_records = 100

    query = LogEntry.objects.all()
    if username:
        query = query.filter(user__username__contains=username)
    for e in query[:num_of_records]:
        print "%s - %s: %s" % (e.action_time, e.user.username, e.change_message)


class Command(BaseCommand):
    help = 'Get the Django History for users.'
    args = '[username - optional] [number of records - optional, default is 100]'

    def handle(self, *args, **options):
        username = None
        if len(args) == 1:
            username = args[0]

        num_of_records = None
        if len(args) > 1:
            num_of_records = args[1]

        history(username, num_of_records)