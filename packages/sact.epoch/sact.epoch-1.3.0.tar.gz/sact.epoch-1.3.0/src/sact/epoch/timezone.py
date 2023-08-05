import datetime
import time

from .interfaces import ITimeZone

from zope.interface import implementer
from zope.component import queryUtility


ZERO = datetime.timedelta(seconds=0)


def is_dst(dt):
    """Return True or False depending of tm_isdst value

    Convert dt in timestamp, and get time object with this timestamp to get
    the localtime and see if this time is dst or not

    """

    tt = (dt.year, dt.month, dt.day,
          dt.hour, dt.minute, dt.second,
          dt.weekday(), 0, -1)
    stamp = time.mktime(tt)

    tt = time.localtime(stamp)
    return tt.tm_isdst > 0


@implementer(ITimeZone)
class UTC(datetime.tzinfo):
    """Represent the UTC timezone.

    From http://docs.python.org/library/datetime.html#tzinfo-objects examples

    XXXvlab: pytz.utc isn't better ?

    """

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        return "<TimeZone: UTC>"


@implementer(ITimeZone)
class TzSystem(datetime.tzinfo):
    """Get the timezone locale of the system. It is used for datetime object.

    This object get the local DST and utcoffset.

    More explanation about how it is work for utcoffset:

    time.daylight is Nonzero if a DST timezone is defined.

    In this case we have two different values in stdoffset and dstoffset.

    For example for timezone 'Europe/Paris' we have:

    stdoffset = -3600
    dstoffset = -7200

    In `utcoffset` method, we check for the daylight saving or not and adjust
    offset in consequence.

    """

    # Get the right offset with DST or not
    stdoffset = datetime.timedelta(seconds=(- time.timezone))
    if time.daylight:
        dstoffset = datetime.timedelta(seconds=(- time.altzone))
    else:
        dstoffset = stdoffset

    # Get the DST adjustement in minutes
    dstdiff = dstoffset - stdoffset

    def utcoffset(self, dt):
        """Return offset of local time from UTC, in minutes"""

        return self.dstoffset if is_dst(dt) else self.stdoffset

    def dst(self, dt):
        """Return the daylight saving time (DST) adjustment, in minutes"""

        return self.dstdiff if is_dst(dt) else ZERO

    def tzname(self, dt):
        """Return time zone name of the datetime object dt"""

        return time.tzname[is_dst(dt)]

    def __repr__(self):
        return "<TimeZone: System>"


@implementer(ITimeZone)
class TzTest(datetime.tzinfo):
    """Timezone crafted for tests"""

    def utcoffset(self, dt):
        return datetime.timedelta(hours=0, minutes=5)

    def tzname(self, dt):
        return "GMT +5m"

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        return "<TimeZone: Test>"


testTimeZone = TzTest()
defaultLocalTimeZone = TzSystem()


def TzLocal():
    """Get local timezone with ZCA"""

    return queryUtility(ITimeZone, name='local', default=defaultLocalTimeZone)
