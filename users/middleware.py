import pytz
from django.utils import timezone
import pytz
from urllib import parse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


# make sure you add `TimezoneMiddleware` appropriately in settings.py
class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware to properly handle the users timezone
    """
    @staticmethod
    def process_request(request):
        try:
            # tzname = request.COOKIES.get('timezone') or settings.TIME_ZONE
            tzname = request.user.time_zone
            timezone.activate(pytz.timezone(parse.unquote(tzname)))
        except:
            timezone.deactivate()
