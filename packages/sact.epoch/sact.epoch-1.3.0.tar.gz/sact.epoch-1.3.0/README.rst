==========
sact.epoch
==========

.. :doctest:

.. image:: http://img.shields.io/pypi/v/sact.epoch.svg?style=flat
   :target: https://pypi.python.org/pypi/sact.epoch/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/sact.epoch.svg?style=flat
   :target: https://pypi.python.org/pypi/sact.epoch/
   :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/0k/sact.epoch/master.svg?style=flat
   :target: https://travis-ci.org/0k/sact.epoch/
   :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/0k/sact.epoch/master.svg?style=flat
   :target: https://coveralls.io/r/0k/sact.epoch
   :alt: Test coverage


``sact.epoch`` is a Python library using Zope Component Architecture providing
legacy ``datetime.datetime`` subclass that allows a simple time abstraction
mecanism, allowing code that would use it as reference to be diverted both
on the local time zone and the real time.


FEATURES
========

using ``sact.epoch.Time``:

- you'll never again hear about "naive" time, a ``Time`` instance
  represents one absolute unique moment, even if you can look at
  these moments through different timezones.
- you will be able to get timestamp of any Time object without thinking about it
  (that was rather complicated with ``datetime``, see:
  http://stackoverflow.com/questions/5067218/get-utc-timestamp-in-python-with-datetime,
  and eventually made it in python 3.3, without clearing all the complexity of naive
  datetimes...
  http://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp,)
- you'll be able to test code that make use of ``.now()`` by setting
  or stopping current time as seen be ``.now()`` function without touching
  at the code. Even more, you'll be able to divert local timezone access easily.

These assumptions are in the code:

- Timestamps are UTC. ``Time`` object are instanced UTC by default
  when not specified otherwise, so ``.fromtimestamp`` and
  ``.utcfromtimestamp`` does the same thing in ``sact.epoch.Time``.
- Time object are considered equal if their timestamp is equal. Note that
  2 ``Time`` instance could be on different timezone and be considered equal.
- ``Time`` object is nothing more than an absolute time reference (a timestamp),
  and a timezone information.
- Access to system information, for instance: call to get the local
  system timezone, and call to get the local system time, should be
  explicit or changeable for tests.  (legacy module ``time`` and
  ``datetime`` will make lot of these calls)


Replaces datetime
-----------------

You can replace ``datetime`` by ``Time``... it has the same API. So you
could instanciate them as you instanciated ``datetime``s::

    >>> from sact.epoch import Time
    >>> Time.now()  # doctest: +ELLIPSIS
    <Time ...+00:00>
    >>> Time(1980, 1, 1)
    <Time 1980-01-01 00:00:00+00:00>

With a difference: there are no naive ``Time``, this means that all
``Time`` objects have a timezone set. By default, it's UTC timezone
that is used.

You could also use a valid ``datetime`` to instanciate a ``Time``
object::

    >>> from sact.epoch.clock import Time, UTC, TzLocal
    >>> from datetime import datetime
    >>> d = datetime(1970, 1, 1, tzinfo=UTC())
    >>> Time(d)
    <Time 1970-01-01 00:00:00+00:00>

Or use ``strptime()``, notice that we need a new ``hint_src_tz`` param,
which informs the code in which timezone the parsed string should be
considered::

    >>> Time.strptime('2000-01-01', '%Y-%m-%d', hint_src_tz=UTC())
    <Time 2000-01-01 00:00:00+00:00>


Manageable clock for tests
--------------------------

There are code that deals with the current system time and
timezone. ``sact.epoch`` will give you mean to divert these calls so
as to fix time and timezone so that test output remain checkable.


Diverting system clock
^^^^^^^^^^^^^^^^^^^^^^

This use zope utilities. We can give a better view thanks to a
manageable clock as time reference::

    >>> from sact.epoch.clock import ManageableClock
    >>> clock = ManageableClock()

We will stop the time to epoch::

    >>> clock.stop()
    >>> clock.ts = 0

And register our clock as the General clock::

    >>> from zope.component import globalSiteManager as gsm
    >>> gsm.registerUtility(clock)

    >>> Time.now()
    <Time 1970-01-01 00:00:00+00:00>


Diverting system timezone
^^^^^^^^^^^^^^^^^^^^^^^^^

Now, let's set our TzTest as local timezone, remember it has 5 minutes
difference to UTC::


    >>> from sact.epoch import testTimeZone
    >>> from sact.epoch.interfaces import ITimeZone

    >>> gsm.registerUtility(testTimeZone, ITimeZone, name='local')


Testing
^^^^^^^

We are now ready to test code::

    >>> Time.now()
    <Time 1970-01-01 00:00:00+00:00>

    >>> Time.now().local
    <Time 1970-01-01 00:05:00+00:05>

As you can see, time has frozen, local time is detected as being our
strange ``testTimeZone`` which is 5 minute ahead.

Remember that in the following tests, local time zone will be the
``testTimeZone``, and the clock is set to EPOCH.


Provides handy shortcuts
------------------------

Instanciation
^^^^^^^^^^^^^

You can instanciate a new ``Time`` with several formats:

With a string (provided you give a timezone in the string or as ``hint_src_tz``)::

    >>> Time("2010-10-01 10:00+01:00")
    <Time 2010-10-01 10:00:00+01:00>
    >>> Time("2010-10-20", hint_src_tz=UTC())
    <Time 2010-10-20 00:00:00+00:00>

With a partial string, remember the we are in::

    >>> Time.now()
    <Time 1970-01-01 00:00:00+00:00>
    >>> Time("10h00", relative=Time.now())
    <Time 1970-01-01 10:00:00+00:00>

If not specified, it uses ``Time.now()`` as reference date to infer
missing element of the given date string::

    >>> Time("Thu 10:36", hint_src_tz=UTC())
    <Time 1970-01-01 10:36:00+00:00>

As it remains a ``datetime.datetime`` sub-class you can instanciate it
like a ``datetime``::

    >>> Time(1980, 1, 2)
    <Time 1980-01-02 00:00:00+00:00>


Properties
^^^^^^^^^^

Getting timestamp from a datetime was nightmarish. Now simply::

    >>> t = Time(1980, 1, 1)
    >>> t.timestamp
    315532800

or (as an alias)::

    >>> t.ts
    315532800

And of course::

    >>> Time.fromtimestamp(t.timestamp) == t
    True

As a matter of fact, ``.fromtimestamp`` is equivalent to
``.utcfromtimestamp``. (Let's repeat it: timestamp should ALWAYS be
considered UTC). If you want system local time from a timestamp you
could::

    >>> Time.fromtimestamp(t.timestamp).local
    <Time 1980-01-01 00:05:00+00:05>

Getting the local/utc zoned time (not changing the time, only the
timezone)::

    >>> t.local, t.utc
    (<Time 1980-01-01 00:05:00+00:05>, <Time 1980-01-01 00:00:00+00:00>)

So to make sure you understood::

    >>> t.local == t.utc
    True
    >>> t.local.timestamp == t.timestamp
    True

This was to illustrate the fact that the time didn't change.

Getting some common representations::

    >>> t.iso
    '1980-01-01 00:00:00+00:00'

This last string formatting of a date is complete, and you can easily get
a accurate ``sact.epoch.Time`` object with it, by direct instanciation:

    >>> Time(t.iso) == t
    True

Warning, these representation will loose the tz info::

    >>> t.short        ## warning: this representation does not include tz info
    '1980-01-01 00:00:00'
    >>> t.local.short  ## warning: this representation does not include tz info
    '1980-01-01 00:05:00'
    >>> t.short_short  ## warning: this representation does not include tz info
    '1980-01-01 00:00'

As they don't provide the timezone's information, you can't instanciate them
directly without providing an hint thanks to giving the timezone, or by giving
a relative datetime from which the timezone will be taken::

    >>> Time(t.short)
    Traceback (most recent call last):
    ...
    ValueError: No timezone hinted, nor found.
    >>> Time(t.short, hint_src_tz=UTC())
    <Time 1980-01-01 00:00:00+00:00>

strptime
^^^^^^^^


``Time.strptime()`` was modified from the ``datetime.datetime``
version, it now asks for the source timezone info::

    >>> Time.strptime('15:08', '%H:%M', hint_src_tz=TzLocal())
    <Time 1900-01-01 15:03:00+00:00>

Notice that the ``Time`` instance is in UTC, so ``15:08`` in implicit
local time zone, became ``15:03`` in UTC. If you wanted the local
``Time`` instance instead::

    >>> Time.strptime('15:08', '%H:%M', hint_src_tz=TzLocal()).local
    <Time 1900-01-01 15:08:00+00:05>

The local timezone detection is of course divertable, and you can
also set it thanks to a new argument named ``hint_src_tz``::

    >>> Time.strptime('15:08', '%H:%M', hint_src_tz=UTC())
    <Time 1900-01-01 15:08:00+00:00>

Notice also, that we didn't specify 1900 as the year, but it was used. In
``Time.strptime()`` you can actually set the reference::

    >>> t = Time(2000, 1, 1)
    >>> Time.strptime('15:08', '%H:%M', hint_src_tz=UTC(), relative=t)
    <Time 2000-01-01 15:08:00+00:00>


How to unregister
----------------------

You can unregister the diverting mecanism::

    >>> TzLocal()
    <TimeZone: Test>
    >>> gsm.unregisterUtility(clock)
    True
    >>> gsm.unregisterUtility(testTimeZone, ITimeZone, 'local')
    True
    >>> TzLocal()
    <TimeZone: System>


INSTALLATION
============

For installation issue please refer to ``INSTALL.rst`` file.


DEVELOPPEMENT
=============

You can test or use this code simply by launching::

    python bootstrap.py
    buildout

This will install all dependency needed by this code to start coding.


TEST
----

Test framework is available through standard z3c.testsetup mecanism::

    bin/test


DOC
---

Complete documentation can be generated thanks to::

    bin/doc
