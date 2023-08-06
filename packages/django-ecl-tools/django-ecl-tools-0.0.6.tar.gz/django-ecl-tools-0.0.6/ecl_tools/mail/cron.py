from django.http import HttpResponse

def process_mail(request):
    
    from ecl_tools.mail.core import process_mail_queue

    count_email, count_sms = process_mail_queue()

    return HttpResponse('Done: %s,%s' % (count_email, count_sms))