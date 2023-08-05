from django.conf import settings

def default(request):

    return {
        'settings': settings,
        'request': request,
        }
