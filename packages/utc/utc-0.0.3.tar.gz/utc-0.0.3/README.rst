UTC
===

It Should Be Easier
~~~~~~~~~~~~~~~~~~~

The current Python landscape doesn't make it simple enough to use timezone
aware timestamps.

It'd be nice if datetime.datetime.now() gave you a timezone-aware datetime in
your current timezone, but it doesn't.

You'd expect datetime.datetime.utcnow() to at least be timezone-aware, right?
No.  There's no tzinfo on the datetime you get back from that function.

The pytz_ package has comprehensive support for time zones, and if you need to
do something complicated, you should use that.  But you don't always need to do
something complicated.  Sometimes you just want UTC.

This package provides syntactic sugar around simple UTC handling that I've
rewritten in too many times in past projects.

Usage
~~~~~

There is a now() function that does the right thing::

    >>> import utc
    >>> utc.now()
    datetime.datetime(2013, 8, 30, 16, 51, 50, 316963, tzinfo=<UTC>)

And a datetime constructor that is UTC by default::

    >>> utc.datetime(1900, 1, 1, 13, 25)
    datetime.datetime(1900, 1, 1, 13, 25, tzinfo=<UTC>)

And a time constructor too::

    >>> utc.time(13, 26, 36)
    datetime.time(13, 26, 36, tzinfo=<UTC>)

That is all.

.. _pytz: https://pypi.python.org/pypi/pytz/
