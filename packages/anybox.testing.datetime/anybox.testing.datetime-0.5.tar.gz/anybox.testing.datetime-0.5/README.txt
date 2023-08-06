anybox.testing.datetime
=======================

This package allows to **cheat with current time** in tests.
It has initially been used in Odoo to test workflows spanning over a long period of time.

Currently it mainly provides a ``datetime.set_now()`` method to fake the
current time, and a ``datetime.real_now()`` to return back to the original
time.

Usage
~~~~~

Before anything, the package must be imported in order to replace the
regular ``datetime`` module with the modified one::

  >>> import anybox.testing.datetime
  >>> from datetime import datetime
  >>> import time

Let's keep the real value of ``now`` around::

  >>> start = datetime.now()
  >>> start_t = time.time()
  >>> start_s = time.strftime('%Y-%m-%d')
  >>> start_l = time.localtime()
  >>> start_c = time.ctime()

Then you can change the current time::

  >>> datetime.set_now(datetime(2001, 01, 01, 3, 57, 0))
  >>> datetime.now()
  datetime(2001, 1, 1, 3, 57)
  >>> datetime.today()
  datetime(2001, 1, 1, 3, 57)

The time module goes along::

  >>> datetime.fromtimestamp(time.time())
  datetime(2001, 1, 1, 3, 57)

Note that you can expect a few microseconds difference (not displayed
here because ``datetime.fromtimestamp`` ignores them).

Some other functions from the time module also return the current time:

  >>> time.localtime()
  time.struct_time(tm_year=2001, tm_mon=1, tm_mday=1, tm_hour=3, tm_min=57, tm_sec=0, tm_wday=0, tm_yday=1, tm_isdst=-1)
  >>> time.strftime('%Y-%m-%d')
  '2001-01-01'
  >>> time.ctime()
  'Mon Jan  1 03:57:00 2001'
  >>> time.asctime()
  'Mon Jan  1 03:57:00 2001'
  >>> time.gmtime()
  time.struct_time(tm_year=2001, tm_mon=1, tm_mday=1, tm_hour=3, tm_min=57, tm_sec=0, tm_wday=0, tm_yday=1, tm_isdst=-1)

The remaining behaviours are not altered

  >>> time.localtime(0).tm_year
  1970
  >>> time.strftime('%Y-%m-%d', datetime(1999,9,9).timetuple())
  '1999-09-09'
  >>> time.ctime(5)
  'Thu Jan  1 02:00:05 1970'
  >>> time.asctime(time.localtime(5))
  'Thu Jan  1 02:00:05 1970'
  >>> time.gmtime(5.0)
  time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=5, tm_wday=3, tm_yday=1, tm_isdst=0)



Don't forget afterwards to get back to the regular system clock, otherwise
many pieces of code might get very suprised if the system clock looks as if
it's frozen::

  >>> datetime.real_now()

Now let's check it worked::

  >>> now = datetime.now()
  >>> now > start
  True
  >>> from datetime import timedelta
  >>> now - start < timedelta(0, 0, 10000) # 10 ms
  True

And with the ``time`` module::

  >>> now_t = time.time()
  >>> now_t > start_t
  True
  >>> now_t - start_t < 0.01 # 10 ms again
  True
  >>> time.strftime('%Y-%m-%d') == start_s
  True
  >>> time.localtime().tm_mday == start_l.tm_mday
  True

Other constructors are still available (this is a non regression
test)::

  >>> import datetime
  >>> datetime.time(3, 57, 0)
  datetime.time(3, 57)
  >>> datetime.datetime(2013, 1, 1, 3, 57, 0)
  datetime(2013, 1, 1, 3, 57)
  >>> datetime.date(2013, 1, 1)
  datetime.date(2013, 1, 1)

Behind the hood
~~~~~~~~~~~~~~~

Our replacement class is the one loaded from the ``datetime`` module,
but instances of the original ``datetime`` class behave exactly as
instances of our ``datetime.datetime``. This is needed because most
computational methods, actually return an object of the original
``datetime`` class. This works with python >= 2.6 only.

First let's check that our class is a subclass of the original
one. If this fails, this test does not mean anything anymore::

  >>> datetime.datetime is datetime.original_datetime
  False
  >>> issubclass(datetime.datetime, datetime.original_datetime)
  True

Then let's demonstrate the behaviour::

  >>> odt = datetime.original_datetime(2012, 1, 1)
  >>> isinstance(odt, datetime.datetime)
  True
  >>> issubclass(datetime.original_datetime, datetime.datetime)
  True

We'll need a ``tzinfo`` subclass from now on.

  >>> from datetime import tzinfo
  >>> class mytzinfo(tzinfo):
  ...     def utcoffset(self, dt):
  ...         return timedelta(hours=2)
  ...     def dst(self, dt):
  ...         return timedelta(0)

Compatibility
~~~~~~~~~~~~~

Over the lifespan of this development toolkit module, we've had to ensure
compatibility with several subsystems

logging
-------

In the logging module, ``time.localtime`` is used as a method. We just check it works

  >>> import logging
  >>> datetime.datetime.set_now(datetime.datetime(2000, 1, 1))
  >>> logging.Formatter().converter().tm_year >= 2014
  True
  >>> datetime.datetime.real_now()

SQLite
------

Also, ``sqlite3`` does recognize our ``datetime`` and ``date`` classes as
if they were the original ones::

  >>> import sqlite3
  >>> cnx = sqlite3.connect(':memory:')
  >>> cr = cnx.cursor()
  >>> cr = cr.execute("CREATE TABLE dates (dt text, d text)")
  >>> dt = datetime.datetime(2013, 1, 25, 12, 34, 0)
  >>> d = datetime.date(2013, 4, 7)
  >>> cr = cr.execute("INSERT INTO dates VALUES (?, ?)", (dt, d))
  >>> cr = cr.execute("SELECT dt, d from dates")
  >>> cr.fetchall()
  [(u'2013-01-25 12:34:00', u'2013-04-07')]

Restore original time
~~~~~~~~~~~~~~~~~~~~~

Now let's try this again with the original ones::

  >>> dt = datetime.datetime.now()
  >>> isinstance(dt, datetime.original_datetime)
  True
  >>> d = datetime.date.today()
  >>> cr = cr.execute("INSERT INTO dates VALUES (?, ?)", (dt, d))
  >>> cr = cr.execute("SELECT dt, d from dates")
  >>> res = cr.fetchall() # can't check the value, it changes a lot !


Data streaming aka pickle
-------------------------

The mock_dt support pickling::

  >>> import pickle
  >>> from StringIO import StringIO
  >>> stream = StringIO()
  >>> v = datetime.datetime(2013, 1, 1, 3, 57, 0)
  >>> pickle.dump(v, stream)
  >>> stream.seek(0)
  >>> v2 = pickle.load(stream)
  >>> v == v2
  True
  >>> type(v2)
  <class 'anybox.testing.datetime.mock_dt.datetime'>
  >>> stream = StringIO()
  >>> v = datetime.datetime.now()
  >>> pickle.dump(v, stream)
  >>> stream.seek(0)
  >>> v2 = pickle.load(stream)
  >>> v == v2
  True
  >>> type(v2)
  <class 'anybox.testing.datetime.mock_dt.datetime'>
  >>> stream = StringIO()
  >>> datetime.datetime.set_now(datetime.datetime(2001, 01, 01, 3, 57, 0))
  >>> v = datetime.datetime.now()
  >>> pickle.dump(v, stream)
  >>> stream.seek(0)
  >>> v2 = pickle.load(stream)
  >>> v == v2
  True
  >>> type(v2)
  <class 'anybox.testing.datetime.mock_dt.datetime'>

Test
~~~~

This README is also a doctest. To test it and other doctests for this package,
simply install Nose and run::

  $ nosetests

