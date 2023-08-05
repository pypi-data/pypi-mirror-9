# -*- coding: utf-8 -*-
"""
.. :doctest:

"""

import datetime
import time
import warnings
import dateutil.parser

from zope.interface import provider, implementer
from zope.component import queryUtility

from .interfaces import ITime, IClock
from .timezone import UTC, TzLocal
from .strptime import strptime
from .utils import dt2ts


try:
    unicode = unicode
except NameError:  ## pragma: no cover
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:  ## pragma: no cover
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


DEFAULT_PARSER_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%m-%d",
    "%m/%d",
    "%m-%d %H:%M:%S",
    "%m-%d %H:%M",
    "%d %H:%M",
    "%d %Hh%M",
    "%d %Hh",
    "%H:%M:%S",
    "%H:%M",
    "%Hh%M",
    "%Hh",
    "%Mm",
    "%M",
    ]


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def deprecate(in_favor=None):

    def decorator(f):

        def wrapped(*args, **kwargs):
            if in_favor:
                deprecation("Call to %r is deprecated, use %r instead."
                            % (f.__name__, in_favor))
            else:
                deprecation("Call to %r is deprecated." % (f.__name__, ))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def round_date(date):
    """Round a timedelta to the last minute (remove seconds and microseconds).

    Setup:

         >>> from sact.epoch import round_date, Time

    Nothing to do:

         >>> round_date(Time(2010, 1, 1, 1, 1, 0))
         <Time 2010-01-01 01:01:00+00:00>

    Round to 1 minute when we have 1 minute and 30 seconds:

         >>> round_date(Time(2010, 1, 1, 1, 1, 30))
         <Time 2010-01-01 01:01:00+00:00>

    """
    assert(isinstance(date, Time))

    if date.second or date.microsecond:
        return date - datetime.timedelta(seconds=date.second,
                                         microseconds=date.microsecond)
    return date


@implementer(IClock)
class Clock(object):
    """Time Factory

    Will only serve the current time.

    Usage
    =====

        >>> from sact.epoch.clock import Clock
        >>> c = Clock()

    We can use property 'ts' to get the timestamp and it should change very
    accurately at each call:

        >>> t1 = c.ts
        >>> t2 = c.ts
        >>> t1 < t2
        True

    If we need a full object we should use:

        >>> c.time
        <Time ...>

    """

    @property
    def time(self):
        """Should return later a Time object"""

        return Time.utcfromtimestamp(self.ts)

    @property
    def ts(self):
        return time.time()


@implementer(IClock)
class ManageableClock(Clock):
    r"""Creates a manageable time object

    Can be used to control what time it is. Start/Stop method can
    start/stop time, and wait/set will alter current time.

    Usage
    =====

        >>> from sact.epoch.clock import ManageableClock
        >>> mc = ManageableClock()

    Stopping time
    -------------

        >>> mc.stop()
        >>> t1 = mc.ts
        >>> t2 = mc.ts
        >>> assert t1 == t2, 'time %r should be equal to %r and it isn\'t' \
        ...              % (t1, t2)
        >>> mc.is_running
        False

    Stoping while running should do nothing:

        >>> mc.stop()
        >>> mc.is_running
        False


    Restarting time
    ---------------

        >>> mc.start()
        >>> t1 = mc.ts
        >>> t2 = mc.ts
        >>> assert t1 != t2, 'time %r should NOT be equal to %r and it is' \
        ...              % (t1, t2)
        >>> mc.is_running
        True

    Restarting while running should do nothing:

        >>> mc.start()
        >>> mc.is_running
        True

        >>> t3 = mc.ts
        >>> assert t1 < t3, \
        ...    'time %r should be superior to %r and it isn\'t' \
        ...    % (t3, t1)


    Setting time
    ------------

        >>> mc.stop()
        >>> mc.ts = 0
        >>> mc.ts
        0
        >>> mc.start()
        >>> ts = mc.ts
        >>> assert ts > 0, \
        ...    'clock should have been running and thus timestamp should be greater than 0.' \
        ...    'It was %r.' % ts

    Altering time
    -------------

        >>> mc.stop()
        >>> mc.ts = 20
        >>> mc.ts += 10
        >>> mc.ts
        30
        >>> mc.start()
        >>> ts = mc.ts
        >>> assert ts > 30, \
        ...    'clock should have been running and thus timestamp should be greater than 30.' \
        ...    'It was %r.' % ts

    Setting time should not stop the clock if it was running:

        >>> mc.ts = 20
        >>> mc.is_running
        True


    Altering with wait
    ------------------

        >>> mc.stop()
        >>> mc.ts = 0
        >>> mc.wait(minutes=5)
        >>> mc.ts
        300
        >>> mc.start()
        >>> mc.wait(minutes=5)
        >>> ts = mc.ts
        >>> assert ts > 600, \
        ...    'clock should have been running and thus timestamp should be greater than 600.' \
        ...    'It was %r.' % ts

    With no specific argument, it'll be casted to int and interpreted
    in seconds:

        >>> mc.stop()
        >>> mc.ts = 0
        >>> mc.wait(3)
        >>> mc.ts
        3


    """

    def __init__(self):
        self.delta = 0
        self._ft = None ## freezed time

    def start(self):
        if self.is_running:
            return
        ## use _ft to calculate the time delta
        self.delta = self.ts - self.delta - self._ft
        self._ft = None

    def stop(self):
        ## save real current time
        self._ft = self.ts - self.delta

    @property
    def is_running(self):
        return self._ft is None

    def get_ts(self):
        if not self.is_running:
            return self._ft
        return time.time() + self.delta

    def set_ts(self, value):
        self.delta = value - time.time()
        # don't forget to update self._ft
        if self._ft is not None:
            self._ft = value

    ts = property(get_ts, set_ts)

    def wait(self, timedelta=None, **kwargs):
        """Provide a convenient shortcut to alter the current time

        timedelta can be an int/float or a timedelta objet from timedelta

        """
        if timedelta is None:
            timedelta = datetime.timedelta(**kwargs)

        if isinstance(timedelta, datetime.timedelta):
            secs = timedelta.days * 86400 + timedelta.seconds
        else:
            secs = int(timedelta)

        self.ts += secs


DefaultClock = Clock()
DefaultManageableClock = ManageableClock()

@provider(ITime)
class Time(datetime.datetime):
    """Time Factory

      Time is an abstraction of a specific point of time. As a subclass of
    datetime, it provides the same functionality. Additionaly it ensures that a
    timezone is always associated to the Time instance, and some simple common
    representation are provided as properties.

      And most important: Time.now() will silently request for the registered
    clock to get time information, allowing to manage time easily.

      Same mecanism is used to get the local time zone, allowing to override
    the detection of the local time zone when using Time.now_lt().


    Limitations
    ===========

      Underlying Datetime object have some methods that can fail after
    initialisation as Datetime.strftime(). Time object make an extensive
    use of some of them and thus will perform a validity check of these
    methods at initialisation time. This will limit the possible range
    of times that is supported currently by the Time object.

      The earlier date possible depends of your architecture. You can set the
    'disable_validity_check' optional argument to 'True' at init time to bypass
    the checkings but notice that some localized methods are then not garanteed
    to work and have reportedly failed on dates earlier than year 1900::

    On python 2:

      # >>> Time(1, 1, 1)
      # Traceback (most recent call last):
      # ...
      # ValueError: Encountered datetime method limitation: ...

    But this does not occur on python 3:

      # >>> Time(1, 1, 1)
      # <Time 0001-01-01 00:00:00+00:00>

    Usage
    =====

    This is quite straightforward to use:

        >>> from sact.epoch import Time
        >>> Time.now()
        <Time ...+00:00>

    Notice that it has a timezone information set. Silently, the current time
    was asked to the registered clock available, which is by default the normal
    clock.


    We can give a better view thanks to a manageable clock as time reference:

        >>> from sact.epoch.clock import ManageableClock
        >>> clock = ManageableClock()

    We will stop the time to epoch:

        >>> clock.stop()
        >>> clock.ts = 0

    Let's set it as reference:

        >>> from zope.component import globalSiteManager as gsm
        >>> gsm.registerUtility(clock)

    Now, let's set our TzTest as local timezone, remember it has 5 minutes
    difference to UTC:

        >>> from sact.epoch import testTimeZone
        >>> from sact.epoch.interfaces import ITimeZone

        >>> gsm.registerUtility(testTimeZone, ITimeZone, name='local')

    Here is the result of each function:

        >>> Time.now()
        <Time 1970-01-01 00:00:00+00:00>

        >>> Time.now_lt()
        <Time 1970-01-01 00:05:00+00:05>

    Please note that there are 5 minutes of diff to UTC


    Instanciation
    =============

    It takes same arguments than datetime legacy object:

        >>> Time(1980, 1, 1)
        <Time 1980-01-01 00:00:00+00:00>

    Notice that in this case, it takes the UTC timezone.

    Additionnaly it can take a real datetime as argument:

        >>> from datetime import datetime
        >>> d = datetime(1970, 1, 1, tzinfo=testTimeZone)
        >>> t = Time(d)
        >>> t
        <Time 1970-01-01 00:00:00+00:05>

        >>> Time(t)
        <Time 1970-01-01 00:00:00+00:05>

    Or even a direct string:

        >>> Time('1970-01-01 00:00:00+00:05')
        <Time 1970-01-01 00:00:00+00:05>

        >>> Time(u'2000-01-01 00:00:00+01:00')
        <Time 2000-01-01 00:00:00+01:00>

    However, if you don't provide the timezone in the string representation
    or in the datetime (which is then called naive-datetimes):

        >>> Time(datetime(1970, 1, 1))
        Traceback (most recent call last):
        ...
        ValueError: No timezone hinted, nor found.

        >>> Time('1970-01-01 00:00:00')
        Traceback (most recent call last):
        ...
        ValueError: No timezone hinted, nor found.

    Hopefully, you can provide an hint to what is the intended timezone:

        >>> from sact.epoch import UTC
        >>> Time(datetime(1970, 1, 1), hint_src_tz=UTC())
        <Time 1970-01-01 00:00:00+00:00>
        >>> Time('2000-01-01 00:00:00', hint_src_tz=UTC())
        <Time 2000-01-01 00:00:00+00:00>

    Additionaly, partial date string parsing is available:

        >>> Time('15:30', hint_src_tz=UTC())
        <Time 1970-01-01 15:30:00+00:00>

    Avoid using more than one argument when providing a string, and be
    careful for instance to name the keyword argument::

        >>> Time('15:30', UTC())
        Traceback (most recent call last):
        ...
        SyntaxError: Too much positional arguments when using Time instanciation by string.


    Representations
    ^^^^^^^^^^^^^^^

    There are several standard representation that are available:

        >>> t.iso
        '1970-01-01 00:00:00+00:05'

    Short local (remove time zone):

        >>> t.short
        '1970-01-01 00:00:00'

    Short short local (remove seconds):

        >>> t.short_short
        '1970-01-01 00:00'

    timetuples:

        >>> t.tt
        time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)

    These are DEPRECATED usage::

        >>> import warnings
        >>> warnings.simplefilter('always')
        >>> t.iso_local
        '1970-01-01 00:00:00+00:05'

    Short local (remove time zone):

        >>> t.short_local
        '1970-01-01 00:00:00'

    Short short local (remove seconds):

        >>> t.short_short_local
        '1970-01-01 00:00'


    Timezone changing
    ^^^^^^^^^^^^^^^^^

    You can change the timezone (without changing the actual stored
    time) of a Time instance by using ``astimezone()`` which stems
    out underlying datetime API. We provide here 2 handy shortcuts:

        >>> Time(1980, 1, 1).local
        <Time 1980-01-01 00:05:00+00:05>
        >>> Time(1980, 1, 1).utc
        <Time 1980-01-01 00:00:00+00:00>

    These are DEPRECATED usage::

        >>> Time(1980, 1, 1).aslocal
        <Time 1980-01-01 00:05:00+00:05>
        >>> Time(1980, 1, 1).asutc
        <Time 1980-01-01 00:00:00+00:00>


    """

    def __new__(cls, *args, **kwargs):
        if len(args) and isinstance(args[0], datetime.datetime):
            return Time.from_datetime(args[0], **kwargs)

        if len(args) and isinstance(args[0], basestring):
            if len(args) > 1:
                raise SyntaxError(
                    "Too much positional arguments when using Time "
                    "instanciation by string.")
            if "hint_src_tz" in kwargs:
                try:
                    return Time.from_string(args[0], **kwargs)
                except ValueError:
                    pass

            if "relative" in kwargs:
                default = kwargs["relative"]
                del kwargs["relative"]
            else:
                ## XXXvlab: hum, we have to craft a Time without timezone
                ## to force error if no explicit timezone is given to the
                ## Time instanciation
                default = Time.now().replace(tzinfo=kwargs.get("hint_src_tz"))

            return Time(dateutil.parser.parse(args[0], default=default),
                        **kwargs)

        if 'tzinfo' not in kwargs and len(args) < 8:
            # XXXjballet: to test
            kwargs['tzinfo'] = UTC()

        check = not kwargs.pop('disable_validity_check', False)

        dt = super(Time, cls).__new__(cls, *args, **kwargs)

        if check:
            ## Check that the architecture can call localized methods
            try:
                dt.strftime('%Y')
            except ValueError as e:  ## pragma: no cover
                raise ValueError("Encountered datetime method limitation:"
                                 " %s" % str(e))

        return dt

    def __repr__(self):
        return "<Time %s>" % self

    @classmethod
    def from_datetime(cls, dt, hint_src_tz=None):
        """Convert a datetime object with timezone to a Time object

        This method provides a handy way to convert datetime objects to Time
        objects:

            >>> import datetime
            >>> from sact.epoch import UTC, TzLocal
            >>> dt = datetime.datetime(2000, 1, 1, tzinfo=UTC())
            >>> Time.from_datetime(dt)
            <Time 2000-01-01 00:00:00+00:00>

        The provided datetime should contain a timezone information or the
        conversion will fail:

            >>> Time.from_datetime(datetime.datetime.now())
            Traceback (most recent call last):
            ...
            ValueError: No timezone hinted, nor found.

        You can provide yourself this timezone information thanks to
        the 'hint_src_tz' argument:

            >>> Time.from_datetime(datetime.datetime(2000, 1, 1),
            ...     hint_src_tz=UTC())
            <Time 2000-01-01 00:00:00+00:00>

        However, this remains an hint, and if timezone can be found in
        the datetime, the 'hint_src_tz' argument will be ignored:

            >>> Time.from_datetime(
            ...      datetime.datetime(2000, 1, 1, tzinfo=UTC()),
            ...      hint_src_tz=TzLocal())
            <Time 2000-01-01 00:00:00+00:00>


        """

        tzinfo = dt.tzinfo if dt.tzinfo else hint_src_tz
        if tzinfo is None:
            raise ValueError("No timezone hinted, nor found.")

        return cls(dt.year, dt.month, dt.day, dt.hour,
                   dt.minute, dt.second, dt.microsecond,
                   tzinfo)

    def __add__(self, delta):
        """Override datetime '+' to return a Time object

        Add a timedelta:

            >>> Time(2010, 1, 1) + datetime.timedelta(days=1)
            <Time 2010-01-02 00:00:00+00:00>

        Add an other Time (send the original exception):

            >>> Time(2010, 1, 1) + Time(1970, 1, 1)
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for +: 'Time' and 'Time'

        """
        d = super(Time, self).__add__(delta)
        if isinstance(d, datetime.datetime):
            return self.from_datetime(d)
        return d

    def __sub__(self, delta):
        """Override datetime '-' to return a Time object

        Sub a timedelta:

            >>> Time(2010, 1, 1) - datetime.timedelta(days=1)
            <Time 2009-12-31 00:00:00+00:00>

        Sub an other Time:

            >>> Time(2010, 1, 2) - Time(2010, 1, 1)
            datetime.timedelta(1)

        """
        d = super(Time, self).__sub__(delta)
        if isinstance(d, datetime.datetime):
            return self.from_datetime(d)
        return d

    @staticmethod
    def now():
        utility = queryUtility(IClock, default=DefaultClock)
        return utility.time.replace(tzinfo=UTC())

    ## XXXvlab: to deprecate
    @staticmethod
    def now_lt():
        return Time.now().local

    @classmethod
    def utcfromtimestamp(cls, ts):
        """Return a UTC datetime from a timestamp.

            >>> Time.utcfromtimestamp(0)
            <Time 1970-01-01 00:00:00+00:00>

        """

        dt = super(Time, cls).utcfromtimestamp(ts)
        return dt.replace(tzinfo=UTC())

    @classmethod
    def fromtimestamp(cls, ts, tz=None):
        """Return a UTC datetime from a timestamp.

            >>> from sact.epoch.timezone import testTimeZone
            >>> Time.fromtimestamp(0, tz=testTimeZone)
            <Time 1970-01-01 00:05:00+00:05>

        """
        t = cls.utcfromtimestamp(ts)
        if tz is not None:
            t = t.astimezone(tz)
        return t

    @classmethod
    def from_string(cls, date_str, hint_src_tz,
                    relative=True, formats=None):
        """Return a UTC datetime from a possibily partial string representation

        By default, output is relative to localtime:

            >>> Time.from_string('15h30', hint_src_tz=UTC())
            <Time 1970-01-01 15:30:00+00:00>

        But it can be specified of course:

            >>> t = Time.from_string('2000-01-01 00:00:00', hint_src_tz=UTC())
            >>> Time.from_string('15h30', hint_src_tz=UTC(),
            ...     relative=t)
            <Time 2000-01-01 15:30:00+00:00>

        """
        formats = formats or DEFAULT_PARSER_FORMATS
        for f in formats:
            try:
                return cls.strptime(
                    date_str, f, hint_src_tz=hint_src_tz,
                    relative=relative)
            except ValueError:
                pass
        raise ValueError("No format seems to know how to parse your string %r"
                         % (date_str, ))

    @classmethod
    def strptime(cls, value, format, hint_src_tz, relative=False):
        """Parse a string to create a Time object.

        hint_src_tz is the source time zone in which the value
        should be interpreted.

        The result Time instance will be in UTC (but you can move it
        with astimezone, or the shortcut '.local').

        Usage
        =====

        source timezone
        ^^^^^^^^^^^^^^^

            >>> from sact.epoch import UTC, TzTest
            >>> Time.strptime('2000-01-01', '%Y-%m-%d', hint_src_tz=UTC())
            <Time 2000-01-01 00:00:00+00:00>

        If source is UTC, then it's the same as the output. No surprise here.

            >>> from sact.epoch.timezone import testTimeZone as ttz

            >>> t0 = Time.strptime('2000-01-01', '%Y-%m-%d',
            ...                    hint_src_tz=ttz)
            >>> t0
            <Time 1999-12-31 23:55:00+00:00>

        If source is in testTimeZone time, then UTC is 5 minutes
        before. The output is by default in UTC. So it's prettier if
        we look at this time in it's original timezone::

            >>> t0.astimezone(ttz)
            <Time 2000-01-01 00:00:00+00:05>

        relative
        ^^^^^^^^

        There's a ``relative`` option which if non-False, will fill
        non given time with the given time instance as relative (or now in
        local time zone if the ``relative`` value is set to True)::

            >>> clock = queryUtility(IClock)

            >>> t1 = Time.strptime('2000-01-01', '%Y-%m-%d', UTC())
            >>> clock.ts = t1.timestamp

        We've just jumped in time and are now at ``t1``. So if we now ask for
        ``strptime()`` in relative mode with only hours and minutes given::

            >>> Time.strptime('15:08', '%H:%M', UTC(), relative=True)
            <Time 2000-01-01 15:08:00+00:00>
            >>> Time.strptime('15:08', '%H:%M', ttz, relative=True)
            <Time 2000-01-01 15:03:00+00:00>

        We could have also set the relative time directly as a value in the
        ``relative`` argument::

            >>> t2 = Time.strptime('1990-05-05', '%Y-%m-%d', UTC())
            >>> Time.strptime('15:08', '%H:%M', ttz, relative=t2)
            <Time 1990-05-05 15:03:00+00:00>

        You can notice how that is different from default behavior, which
        takes EPOCH as relative::

            >>> Time.strptime('15:08', '%H:%M', UTC(), relative=False)
            <Time 1900-01-01 15:08:00+00:00>

        """
        if relative is False:
            dt = super(Time, cls).strptime(value, format)
            dt = dt.replace(tzinfo=hint_src_tz)
            return dt.utc

        relative = Time.now() if relative is True else relative

        input_time = relative.timetuple(), relative.microsecond
        time_struct, microseconds = strptime(value, format,
                                             reference=input_time)
        dt = Time(*time_struct[:6])
        dt = dt.replace(microsecond=microseconds, tzinfo=hint_src_tz)
        return dt.utc

    def astimezone(self, tz):
        """Convert Time object to another timezone and return a Time object

        This overrides the datetime's method to return a Time object instead of
        a datetime object:

            >>> from sact.epoch.timezone import testTimeZone
            >>> type(Time.now().astimezone(testTimeZone))
            <class 'sact.epoch...Time'>

        """

        dt = super(Time, self).astimezone(tz)
        return self.from_datetime(dt)

    @property
    def timestamp(self):
        """Convert this Time instance in a unix timestamp in UTC

        See sact.epoch.utils

            >>> Time(1970, 1, 1, 0, 0, 1).timestamp
            1

        """
        return dt2ts(self)

    @property
    def utc(self):
        return self.astimezone(UTC())

    @property
    def local(self):
        return self.astimezone(TzLocal())

    @property
    def iso(self):
        """Return the iso format in local time

            >>> Time(1970, 1, 1, 1, 1).iso
            '1970-01-01 01:01:00+00:00'

        """
        return self.isoformat(" ")

    @property
    def short(self):
        """Return as iso with without time zone

        Warning, this looses the time zone information and thus could
        be dangerous. Make sure that if you store this, the time zone is
        clearly inferable from its environment.

            >>> Time(1970, 1, 1, 1, 1).short
            '1970-01-01 01:01:00'

        """
        return self.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def short_short(self):
        """Idem without seconds

        Warning, this looses the time zone information and thus could
        be dangerous. Make sure that if you store this, the time zone is
        clearly inferable from its environment.

            >>> Time(1970, 1, 1, 1, 1).short_short
            '1970-01-01 01:01'

        """
        return self.strftime('%Y-%m-%d %H:%M')

    @property
    def tt(self):
        """Returns the timetuple of current Time instance"""
        return self.timetuple()

    ts = timestamp

    ##
    ## DEPRECATED
    ##

    @property
    @deprecate(in_favor='local')
    def aslocal(self):
        return self.local

    @property
    @deprecate(in_favor='utc')
    def asutc(self):
        return self.utc

    @deprecate(in_favor='.local.strftime')
    def strftime_local(self, *args, **kwargs):
        return self.local.strftime(*args, **kwargs)

    @property
    @deprecate(in_favor='.local.iso')
    def iso_local(self):
        return self.local.isoformat(" ")

    @property
    @deprecate(in_favor='.local.short')
    def short_local(self):
        return self.local.strftime('%Y-%m-%d %H:%M:%S')

    @property
    @deprecate(in_favor='.local.short_short')
    def short_short_local(self):
        return self.local.strftime('%Y-%m-%d %H:%M')


"""
Let's unregister the test Timezone and test Clock:

    >>> gsm.unregisterUtility(clock)
    True

    >>> gsm.unregisterUtility(testTimeZone, ITimeZone, 'local')
    True

"""
