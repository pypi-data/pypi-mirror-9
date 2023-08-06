
from ecl_tools.config.autoconf import check_defaults as config_check_defaults

class AutoConfMiddleware:
    """
    This middleware looks for the autoconf flag and then configures the database defaults.
    This must appear after the session
    """

    def process_request(self, request):
        if request.GET.get('autoconf', None) == '1':
                config_check_defaults()




