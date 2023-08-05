
from zope.interface import Interface, Attribute


class ITimeZone(Interface):
    """Standard TimeZone interface as defined in datetime module"""

    def utcoffset(dt):
        """Return offset of local time from UTC, in minutes"""

    def dst(dt):
        """Return the daylight saving time (DST) adjustment, in minutes"""

    def tzname(dt):
        """Return the time zone name corresponding to the datetime object dt"""


class ITime(Interface):
    """Factory to make time object.

    minimal interface

    """

    def now():
        """Return a time object that represent the current time"""


class IClock(Interface):
    """Factory to make time object.

    minimal interface

    """

    def time():
        """Return a time object that represent the current time"""


class IManageableClock(IClock):

    is_running = Attribute(
        u"Freeze the return result of now() command")

    def set(date):
        """Set the result of now() command to date"""

    def stop():
        """Freeze the return result of now() command"""

    def start():
        """Unfreeze the return result of now() command"""

    def wait(timelapse=None, days=0, hours=0, minutes=0, seconds=0):
        """Shortcut to alter_now relative

        Should accept negative value also.

        """
