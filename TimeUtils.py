"""General tools for calculating timezone values as it can get complicated"""
import datetime
import pytz
from tzlocal import get_localzone


class TimeUtils(object):
    """ General utils for calculating offset time"""
    def __init__(self):
        pass

    @classmethod
    def get_start_of_tomorrow_utc(cls):
        """ Returns start of tomorrow in UTC.
        eg: if it's 8pm now in Sydney 1 June 2018,
        it will return 12am Sydney 2 June 2018 in UTC time
        (ie: June 1st 14:00 +00:00)
        """
        local_tz = get_localzone()
        temp_tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        tomorrow = datetime.datetime.combine(temp_tomorrow, datetime.time.min)
        tomorrow = local_tz.localize(tomorrow)
        return tomorrow.astimezone(pytz.utc)

    @classmethod
    def get_end_of_tomorrow_utc(cls):
        """ Returns end of tomorrow in UTC.
        eg: if it's 8pm now in Sydney 1 June 2018,
        it will return 11.59pm Sydney 2 June 2018 in UTC time
        (ie: June 2nd 13:59 +00:00)
        """
        local_tz = get_localzone()
        temp_tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        tomorrow = datetime.datetime.combine(temp_tomorrow, datetime.time.max)
        tomorrow = local_tz.localize(tomorrow)
        tomorrow.astimezone(pytz.utc)
        return tomorrow.astimezone(pytz.utc)
