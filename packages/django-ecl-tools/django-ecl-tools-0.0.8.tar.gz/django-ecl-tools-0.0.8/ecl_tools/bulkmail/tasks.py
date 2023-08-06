import requests
import logging

from celery.task import task

from django.conf import settings

logger = logging.getLogger(__name__)

import time


@task
def mailgun_send(url, data=None):
    count = 0

    auth = data['auth']
    del data['auth']

    while 1:
        count += 1

        try:
            if getattr(settings, 'BULKMAIL_TEST_MODE', False):
                break #don't send mail in test mode; this is for unit testing

            result = requests.post(url, auth=auth, data=data)

        except Exception, e:
            logger.exception(e)


        else:
            if result.status_code in [400]:
                if "'to' parameter is not a valid address" in result.content:
                    logger.error(result.content)
                    break

            if result.status_code == 200:
                break

            else:
                logger.error('Send error: Status Code: %d; Content: %s' % (result.status_code, result.content))

        if count >= 3:
            logger.error("MailGun send failed 3 times. Quiting.")
            break


        time.sleep(1)