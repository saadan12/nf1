from pytz import timezone
from datetime import datetime
from django.conf import settings
from urllib import parse


def common_variables(request):
    tzname = request.COOKIES.get('timezone') or settings.TIME_ZONE
    # tzname = request.user.username
    return {
       "get_current_timezone": datetime.now(timezone(parse.unquote(tzname))).tzname()
    }
