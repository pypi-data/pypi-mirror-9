aiorwlock
=========
.. image:: https://travis-ci.org/aio-libs/aiorwlock.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aiorwlock
.. image:: https://coveralls.io/repos/jettify/aiorwlock/badge.png?branch=master
    :target: https://coveralls.io/r/aio-libs/aiorwlock?branch=master

Read write lock for asyncio_ . A ``RWLock`` maintains a pair of associated
locks, one for read-only operations and one for writing. The read lock may be
held simultaneously by multiple reader tasks, so long as there are
no writers. The write lock is exclusive.

Whether or not a read-write lock will improve performance over the use of
a mutual exclusion lock depends on the frequency that the data is *read*
compared to being *modified*. For example, a collection that is initially
populated with data and thereafter infrequently modified, while being
frequently searched is an ideal candidate for the use of a read-write lock.
However, if updates become frequent then the data spends most of its time
being exclusively locked and there is little, if any increase in concurrency.


Implementation almost direct port from this patch_.


Example
-------

.. code:: python

    import asyncio
    import aiorwlock
    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        rwlock = aiorwlock.RWLock(loop=loop)
        with (yield from rwlock.writer_lock):
            # or same way you can acquire reader lock
            # with (yield from rwlock.reader_lock): pass
            print("inside writer_lock")
            yield from asyncio.sleep(0.1, loop=loop)

    loop.run_until_complete(go())

License
-------

``aiorwlock`` is offered under the Apache 2 license.


.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _patch: http://bugs.python.org/issue8800
