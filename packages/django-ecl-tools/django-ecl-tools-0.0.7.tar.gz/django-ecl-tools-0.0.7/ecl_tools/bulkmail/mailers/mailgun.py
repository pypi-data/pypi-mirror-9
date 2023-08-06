import json

from django.conf import settings
from django.http import HttpResponse

from ecl_tools.bulkmail.mailers.base import BaseEmailer
from ecl_tools.bulkmail.tasks import mailgun_send


class RejectEventResponse(HttpResponse):
    """
    If Mailgun receives a 406 (Not Acceptable) code, Mailgun will determine the POST is rejected and not retry.
    http://documentation.mailgun.com/user_manual.html#webhooks
    """
    status_code = 406


def do_send(mail_domain, data):
    #if we're in debug, send it directly: otherwise queue it
    if getattr(settings, "DEBUG", False) or getattr(settings, "MAILGUN_DISABLE_QUEUE_SEND", False):
        mailgun_send("https://api.mailgun.net/v2/%s/messages" % mail_domain, data=data)
    else:
        mailgun_send.delay("https://api.mailgun.net/v2/%s/messages" % mail_domain, data=data)


class EMailer(BaseEmailer):
    def __init__(self, *args, **kwargs):
        super(EMailer, self).__init__(*args, **kwargs)

    #TODO: is this needed? best practice?
    # def headers(self, unsubscribe):
    #     h = {
    #         'h:List-Id': self.list_id,
    #         'h:List-Unsubscribe': '<%s>' % unsubscribe,
    #     }
    #     return h

    def send(self, context, log=True):
        data = {'auth': ('api', settings.MAILGUN_API_KEY)}
        data.update(context)

        max_batch = 1000

        if 'recipient-variables' in data:

            if not isinstance(data['recipient-variables'], dict):
                raise Exception('recipient-variables must be a dictionary.')

            keys = data['recipient-variables'].keys()

            for i in range(0, len(keys), max_batch): #chunk the keys array by 1000 items
                print len(keys[i:i+max_batch]) #for each chunk, include only the keys within that chunk

                to = []
                recipient_variables = {}
                for key in keys[i:i+max_batch]:
                    to += [key]
                    recipient_variables.update({key: data['recipient-variables'][key]})

                new_data = data.copy()

                new_data['to'] = to
                #recipient-variables needs to be JSON
                new_data['recipient-variables'] = json.dumps(recipient_variables)

                do_send(self.mail_domain, new_data)

                #if log:
                #    self.log_send(email)
        else:
            do_send(self.mail_domain, data)


    def close(self):
        pass
  