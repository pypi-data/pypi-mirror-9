
.. :doctest:

This packages provides a time abstraction mecanism, allowing code that would
use it as reference to be diverted both on the local time zone and the real
time.

This allows clock-dependent code to be tested. See Getting started section for
a more thorough explanation.

Additionnaly, as an abstraction of the legacy datetime object, Time object
provided in ``sact.epoch.Time`` provides some common helpers and force this
object to always provide a timezone.

``sact.epoch`` objects will be of some help:

- if your application manage 2+ different timezones (ie: UTC and local
  timezone), and you are tired of legacy "naive" datetime object on this matter.

- if you want to be able to divert system calls to local time, or
  local time zone of your application for test purpose.


Contents
--------

Time

   subclass of ``datetime``, represent an absolute instant of time (with
   timezone). It forces ``datetime`` usage to be aware of the
   timezone. Additionally, Time.now() will ask the Zope Component Architecture
   registry for a Clock Utility to provide the real time.

Clock

   Clock objects are general reference for getting Time object. The default
   clock is our common normal clock, but ZCA allows to substiture the reference
   and provide other type of Clock as ``sact.epoch.ManageableClock`` which can
   be managed (this means it can be stopped, set, translated in the future or
   the past).

TimeZone

   TimeZone objects represents a specific timezone, ``sact.epoch.TzLocal()``
   will get the local system time zone. This call can be diverted also via the
   ZCA to provide another TimeZone. ``sact.epoch.testTimeZone`` is a common
   divert target timezone that is provided to help testing code.


Getting started
---------------

``sact.epoch.Time`` is meant as a replacement of ``datetime.datetime``. As a
subclass of this later one, it'll provide the same functionality, and thus can
be used almost anywhere you are using ``datetime.datetime``.

Additionaly, using ``sact.epoch.Time`` ensures that:

- all instances will get a time zone. Which isn't the case for ``datetime``
  objects.

- ``.now()`` method will use the Zope Component Architecture registry to get
  a common Utility that is in charge of giving the real time. This allows
  simple overriding mecanism.


Get timestamp from a datetime
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say you have some code using ``datetime.datetime.now()``::

  >>> import datetime
  >>> now = datetime.datetime.now()

First issue: if this variable is meant to represent a time stored as UTC in a
database.

How do you get UTC timestamp from datetime ? (cf:
http://bugs.python.org/issue1457227)

This is a common question. (cf:
http://stackoverflow.com/questions/5067218/get-utc-timestamp-in-python-with-datetime/5499906#5499906)

The answer is ``datetime.datetime`` objects can be naive, which means unaware
of the timezone. Thus, it is impossible to get UTC timestamp from this form of
datetime unless you can guess the timezone yourself.

Hopefully, the timezone of your system didn't change between the datetime
object creation and the moment you want to get a timestamp, if this is the case
you can safely use::

  >>> import sact.epoch.utils
  >>> utc_timestamp = sact.epoch.utils.dt2ts(now)

``dt2ts`` will ask your system for the number of seconds between EPOCH
in the current timezone and the provided datetime. This is why you
must ensure that datetime object was created when the same TimeZone on
the system than when you run this function.

No doctest is given to your eyes on the content of the variable
``utc_timestamp`` because the output depends on the current time. And this
can be often an issue you'll encounter: having complex code that depends on
the current date, how do you test it ? This is the purpose of sact.epoch.Time.


Forcing to use only aware datetime
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quite quickly, you'll ask yourself: but what use have I of naive
``datetime.datetime`` objects if they can't be used in lots of cases ?

The answer is: there are no use of naive ``datetime.datetime``.

Aware datetime objects as ``sact.epoch.Time`` contains all additional
information allowing to:

- get an UTC timestamp
- compare two ``Time`` object whatever there timezone is.

Using naive datetime might even be concidered
harmfull. ``sact.epoch.Time`` will ensure that all your objects are
timezone aware. By default, TimeZone won't even be dependent of your
system local time, but will be stored in UTC timezone.

datetime objects::

  >>> from __future__ import print_function

  >>> print(repr(datetime.datetime.now().tzinfo))
  None
  >>> print(repr(datetime.datetime(1970, 1, 1, 1, 1).tzinfo))
  None

In comparison, ``sact.epoch.Time`` object will always set a timezone::

  >>> print(repr(sact.epoch.Time.now().tzinfo))
  <TimeZone: UTC>
  >>> print(repr(sact.epoch.Time(1970, 1, 1, 1, 1).tzinfo))
  <TimeZone: UTC>

Of course, as Time object is aware, a simple ``timestamp`` property is
available::

  >>> epoch = sact.epoch.Time(1970, 1, 1, 0, 0)
  >>> epoch.timestamp
  0


Diverting time
~~~~~~~~~~~~~~

If you use ``sact.epoch.Time.now()`` in place of
``datetime.datetime.now()``, your code will have seams to divert real
time reference without touching the system clock.

Say your code is::

  >>> db_timestamp = epoch.timestamp
  >>> def is_it_ok():
  ...    now = sact.epoch.Time.now().timestamp
  ...    print(0 == ((now - db_timestamp) % 2))

``is_it_ok`` function code should print ``True`` if number of seconds between
now and epoch is odd.

This is the type of function which is quite difficult to test if you are using
``datetime.datetime.now()``. Whole application will make extensive usage of the
system clock, and will eventually be difficult to test unless you used
``sact.epoch.Time.now()`` in place of datetime.

Here's the test of the function::

  >>> clock = sact.epoch.clock.ManageableClock()

By default, the clock is following the system clock. Let's stop it and set it
to epoch (more on manageable clock in the docstring of the class
ManageableClock)::

  >>> clock.stop()
  >>> clock.ts = 0

Now let's use ZCA to declare this clock as new reference clock::

  >>> from zope.component import globalSiteManager as gsm
  >>> gsm.registerUtility(clock)

We are ready to test the function::

  >>> sact.epoch.Time.now().timestamp
  0
  >>> is_it_ok()
  True

  >>> clock.ts = 1
  >>> sact.epoch.Time.now().timestamp
  1
  >>> is_it_ok()
  False

Please note that ``ManageableClock`` have a ``wait`` method::

  >>> clock.wait(minutes=1)
  >>> sact.epoch.Time.now().timestamp
  61
  >>> is_it_ok()
  False

Of course, the execution of ``clock.wait`` is immediate. You can use a
``datetime.timedelta`` as argument of wait or any keyword args you would send
to ``datetime.timedelta`` constructor (this includes ``days``, ``seconds``,
``microseconds``, ``milliseconds``, ``minutes``, ``hours``, ``weeks`` as of
python version 2.7.1, cf:
http://docs.python.org/library/datetime.html#datetime.timedelta)


Diverting timezone of system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When displaying times to the user, it is appreciated to show the time in local
timezone::

  >>> def what_time_is_it():
  ...     print(sact.epoch.Time.now().local.iso)

Notice the use of the property ``local`` which returns a new ``Time``
instance set to the same moment in time but in the system local
timezone, and the ``iso`` property which returns the iso string 
representation of the ``Time`` object.

The ``local`` property uses ``sact.epoch.TzLocal()`` which is responsible of giving
the system local timezone:

  >>> sact.epoch.TzLocal()
  <TimeZone: System>

Let use the ZCA to divert the TzLocal mechanism to get the system local::

  >>> from sact.epoch import testTimeZone
  >>> from sact.epoch.interfaces import ITimeZone

  >>> gsm.registerUtility(testTimeZone, ITimeZone, name='local')

Now we can test our function::

  >>> clock.ts = 0
  >>> what_time_is_it()
  1970-01-01 00:05:00+00:05

The testTimeZone used is very special and recognizable on purpose: it has
a constant +5 minute offset on UTC.

Internally, call to ``TzLocal()`` has been diverted::

  >>> sact.epoch.TzLocal()
  <TimeZone: Test>


