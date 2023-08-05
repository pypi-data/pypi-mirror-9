import datetime

from dcbase.apps import TIMEZONE_SESSION_KEY
from django.utils import timezone


class DcBaseMiddleware(object):
    def process_request(self, request):
        timezone_name = request.session.get(TIMEZONE_SESSION_KEY)
        if timezone_name:
            timezone.activate(timezone_name)
            return

        try:
            tzoffset = int(request.COOKIES.get('_tz_offset'))
            delta = datetime.timedelta(minutes=0-tzoffset)
            tz = datetime.timezone(delta)
            timezone.activate(tz)
            return
        except ValueError:
            pass

        timezone.deactivate()
