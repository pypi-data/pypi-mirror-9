import logging

logger = logging.getLogger('django')

def raven_test(request):
    from django import http
    if request.user and request.user.is_superuser:

        if 'exception' in request.REQUEST:
            raise Exception('testing123')
        else:
            logger.exception(Exception('log exception 123'))
            return http.HttpResponse('OK')
    else:
        raise http.Http404()
