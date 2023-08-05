
Frozendate: stop time for your tests
====================================

Frozendate suspends time while your tests run.

Frozendate mocks ``datetime.datetime`` and ``datetime.date`` to provide known
times when testing.

Usage
-----

::

    import frozendate

    with frozendate.freeze(1999, 1, 1):
        party_like_its_1999()

    # freeze relative freezes time relative to the current date...
    with freeze_relative(days=-1):
        assert all_my_troubles_seemed_so_far_away()

    with freeze(1999, 12, 31):
        # ...or relative to the previous freeze
        with freeze_relative(days=1):
            print "happy new year!"


Normally time doesn't actually stop when you use freeze – it just starts 
again from the fixed point you specify, eg::

    >>> import frozendate
    >>> import datetime
    >>> with frozendate.freeze(2000, 1, 1):
    ...     print datetime.now().replace(microsecond=0)
    ...     time.sleep(1)
    ...     print datetime.now().replace(microsecond=0)
    ...
    2000-01-01 00:00:00
    2000-01-01 00:00:01

But you can always get the same value back if you pass ``hard=True``::

    >>> with frozendate.freeze(2000, 1, 1, hard=True):
    ...     print datetime.now().replace(microsecond=0)
    ...     time.sleep(1)
    ...     print datetime.now().replace(microsecond=0)
    ...
    2000-01-01 00:00:00
    2000-01-01 00:00:00


Instead of a context manager there are also regular patch and unpatch
functions.
These are useful in test case setup/teardown methods::

    def setUp(self):
        frozendate.patch(2000, 1, 1)

    def tearDown(self):
        frozendate.unpatch()

When you call freeze or patch, it freezes time for all modules found in
``sys.modules``.
Sometimes you want to restrict to a few named modules::

    frozendate.freeze(modules=['mypackage.mymodule'])

Or patch everything, but exclude a few modules that need the real datetime
still::

    frozendate.freeze(dontpatch=['somemodule', 'someotherpackage'])
