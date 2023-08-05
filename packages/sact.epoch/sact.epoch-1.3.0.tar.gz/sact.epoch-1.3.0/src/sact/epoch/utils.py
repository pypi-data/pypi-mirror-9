# -*- coding: utf-8 -*-
"""
.. :doctest:

These small functions deal with 3 time representation without timezone
information.  It is probably simpler to think them as being all UTC.

ISO (abbreviated 'iso')

    Which is a string representation. ie: '2008-11-01 10:00:00'

time tuples (abbreviated 'tt')

    Which are 9-tuples of the form (ie: (2008, 11, 01, 10, 0, 0))

timestamp (abbreviated 'ts')

    Which is the number of seconds since EPOCH. (ie: 1225533600)


"""

import time
import datetime
import calendar


def dt2ts(dt):
    """Converts a datetime object to timestamp

    Important note: naive datetime are supported and are considered
    UTC.

    Usage
    =====

        >>> from sact.epoch import dt2ts
        >>> from sact.epoch import tt2ts, TzLocal, UTC
        >>> import datetime

        >>> epoch = datetime.datetime(1970,1,1)
        >>> dt2ts(epoch)
        0

    This works also with non-naive datetime, and will output
    the right timestamp.

        >>> dt = epoch.replace(tzinfo=UTC())
        >>> dt2ts(dt)
        0

    ``.astimezone()`` will change only the timezone, keeping the real
    moment in time. So timestamp should not change:

        >>> dt2ts(dt.astimezone(TzLocal()))
        0

    """
    return int(tt2ts(dt.utctimetuple()))


def ts2iso(ts):
    """Returns an (UTC) ISO representation of a timestamp

        >>> from sact.epoch import iso2ts, ts2iso

        >>> ts2iso(iso2ts('2008-11-01 10:00:00'))
        '2008-11-01 10:00:00'

    """
    return datetime.datetime.utcfromtimestamp(ts).isoformat(" ")


def iso2ts(iso):
    """Returns a timestamp from an (UTC) ISO representation

    Note that it doesn't take into account local representation.

        >>> from sact.epoch import iso2ts, ts2tt

    EPOCH should return 0 as expected:

        >>> iso2ts('1970-01-01 00:00:00')
        0

    And with any date, we should be able to reconstruct it:

        >>> ts2tt(iso2ts('2008-12-06 12:17:31'))[0:6]
        (2008, 12, 6, 12, 17, 31)

    """

    return tt2ts(time.strptime(iso + " UTC", "%Y-%m-%d %H:%M:%S %Z"))


tt2ts = calendar.timegm
ts2tt = time.gmtime
