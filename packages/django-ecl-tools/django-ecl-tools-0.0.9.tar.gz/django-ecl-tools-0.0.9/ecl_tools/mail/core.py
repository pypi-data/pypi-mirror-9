import logging
import re

from django.core.mail import EmailMessage
from django.conf import settings

from ecl_tools.config.models import GlobalConfig
from .models import MailMessage, SMSMessage

valid_phone_pattern = re.compile('[^0-9]')

def make_valid_phone(phone):
    return valid_phone_pattern.sub("", phone).lstrip('1')[:10]

def send_mail(subject, message, from_email, recipient_list):
    """
    Queue email in MailMessage model.
    """

    if isinstance(recipient_list, list):
        recipient_list = ';'.join(recipient_list)

    #demo override for testing purposes
    demo_to = GlobalConfig.get_or_none('demo_mail_emails')
    if demo_to:
        recipient_list = demo_to

    return MailMessage.objects.create(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
    )

def send_sms(message, from_phone, to):

    """
    Queue sms in SMSMessage model.
    """

    #demo override for testing purposes
    demo_to = GlobalConfig.get_or_none('demo_sms_phone')
    if demo_to:
        to = demo_to

    return SMSMessage.objects.create(
        message=message,
        from_phone=from_phone,
        to=to,
    )


def process_mail_queue():
    """
    Filter all messages of status=active and attempt to send them. Save all exceptions status_details and log.
    :return: Count of active records processed.
    """

    count_email = 0
    for msg in MailMessage.objects.filter(status=1): #get all active emails in queue
        try:
            recipient_list = msg.recipient_list.split(';')
            outbound = EmailMessage(from_email=msg.from_email, to=recipient_list, subject=msg.subject, body=msg.message)
            outbound.content_subtype = "html"
            outbound.send()
            msg.status = 2 #done
            msg.status_details = None
        except Exception, e:
            logging.error('Error sending email: %s' % e)
            msg.status = 3 #error
            msg.status_details = e

        msg.save()
        count_email += 1


    count_sms = 0
    for msg in SMSMessage.objects.filter(status=1): #get all active sms in queue
        try:
            from twilio.rest import TwilioRestClient
            client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            client.messages.create(
                to=make_valid_phone(msg.to),
                from_=make_valid_phone(msg.from_phone),
                body=msg.message
            )
            msg.status = 2 #done
            msg.status_details = None
        except Exception, e:
            logging.error('Error sending sms: %s' % e)
            msg.status = 3 #error
            msg.status_details = e

        msg.save()
        count_sms += 1

    return count_email, count_sms
