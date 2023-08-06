from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from ecl_tools.mail.core import process_mail_queue

@staff_member_required
def process_mail(request):

    count = 0
    if request.GET.get('process', False):
        count = process_mail_queue()

    #TODO: this returns with ?e=1
    #return HttpResponseRedirect('/dj-admin/mail/mailmessage/?processed=%s' % count)
    return HttpResponseRedirect('.')