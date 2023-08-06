Historydb-python
----------------

`Historydb <https://github.com/reverbrain/historydb>`_ client implemented in Python.

It implements C++ API with some pythonic additions, such as iterators and helper functions.

Also it contains client which can use `gevent <http://www.gevent.org/>`_ or threads and handles reconnects and retries.

Requires ``elliptics=2.25.*`` system package (with Python bindings).

To run tests::

    $ python bootstrap.py
    $ bin/buildout
    $ bin/nosetests


For elliptics=2.24.* use v0.3.0
