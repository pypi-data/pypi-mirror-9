=======================
Couchbase Python Client
=======================

Client for Couchbase_.

.. image:: https://travis-ci.org/couchbase/couchbase-python-client.png
    :target: https://travis-ci.org/couchbase/couchbase-python-client

-----------------------
Building and Installing
-----------------------

This only applies to building from source. If you are using a Windows
installer then everything (other than the server) is already included.
See below for windows snapshot releases.

Also note that these instructions apply to building from source.
You can always get the latest supported release version from
`PyPi <http://pypi.python.org/pypi/couchbase>`_

~~~~~~~~~~~~~
Prerequisites
~~~~~~~~~~~~~

- Couchbase Server (http://couchbase.com/download)
- libcouchbase_. version 2.1.0 or greater (Bundled in Windows installer)
- libcouchbase development files.
- Python development files
- A C compiler.

~~~~~~~~
Building
~~~~~~~~

.. code-block:: sh

    python setup.py build_ext --inplace


If your libcouchbase install is in an alternate location (for example,
`/opt/local/libcouchbase`), you may add extra directives, like so

.. code-block:: sh

    python setup.py build_ext --inplace \
        --library-dir /opt/local/libcouchbase/lib \
        --include-dir /opt/local/libcouchbase/include

Or you can modify the environment ``CFLAGS`` and ``LDFLAGS`` variables.

.. _windowsbuilds:

~~~~~~~~~~~~~~~~~
Windows Snapshots
~~~~~~~~~~~~~~~~~

A list of recent snapshot builds for Windows may be found
`here <http://packages.couchbase.com/clients/python/snapshots>`.

You can always get release binaries from PyPi (as above).

-----
Using
-----

Here's an example code snippet which sets a key and then reads it

.. code-block:: pycon

    >>> from couchbase import Couchbase
    >>> c = Couchbase.connect(bucket='default')
    >>> c
    <couchbase.connection.Connection bucket=default, nodes=['127.0.0.1:8091'] at 0xb21a50>
    >>> c.set("key", "value")
    OperationResult<RC=0x0, Key=key, CAS=0x31c0e3f3fc4b0000>
    >>> res = c.get("key")
    >>> res
    ValueResult<RC=0x0, Key=key, Value=u'value', CAS=0x31c0e3f3fc4b0000, Flags=0x0>
    >>> res.value
    u'value'
    >>>

You can also use views

.. code-block:: pycon

    >>> from couchbase import Couchbase
    >>> c = Couchbase.connect(bucket='beer-sample')
    >>> resultset = c.query("beer", "brewery_beers", limit=5)
    >>> resultset
    View<Design=beer, View=brewery_beers, Query=Query:'limit=5', Rows Fetched=0>
    >>> for row in resultset: print row.key
    ...
    [u'21st_amendment_brewery_cafe']
    [u'21st_amendment_brewery_cafe', u'21st_amendment_brewery_cafe-21a_ipa']
    [u'21st_amendment_brewery_cafe', u'21st_amendment_brewery_cafe-563_stout']
    [u'21st_amendment_brewery_cafe', u'21st_amendment_brewery_cafe-amendment_pale_ale']
    [u'21st_amendment_brewery_cafe', u'21st_amendment_brewery_cafe-bitter_american']

~~~~~~~~~~~
Twisted API
~~~~~~~~~~~

The Python client now has support for the Twisted async network framework.
To use with Twisted, simply import ``txcouchbase.connection`` instead of
``couchbase.Couchbase``

.. code-block:: python

    from twisted.internet import reactor
    from txcouchbase.connection import Connection as TxCouchbase

    cb = TxCouchbase(bucket='default')
    def on_set(ret):
        print "Set key. Result", ret

    def on_get(ret):
        print "Got key. Result", ret
        reactor.stop()

    cb.set("key", "value").addCallback(on_set)
    cb.get("key").addCallback(on_get)
    reactor.run()

    # Output:
    # Set key. Result OperationResult<RC=0x0, Key=key, CAS=0x9a78cf56c08c0500>
    # Got key. Result ValueResult<RC=0x0, Key=key, Value=u'value', CAS=0x9a78cf56c08c0500, Flags=0x0>


The ``txcouchbase`` API is identical to the ``couchbase`` API, except that where
the synchronous API will block until it receives a result, the async API will
return a `Deferred` which will be called later with the result or an appropriate
error.

~~~~~~~~~~
GEvent API
~~~~~~~~~~

The `experimental_gevent_support` constructor flag has now been removed. Instead,
you can import the `gcouchbase.connection` package and use the `GConnection`
class like so:

.. code-block:: python

    from gcouchbase.connection import GCouchbase
    conn = GCouchbase(bucket='default')
    print conn.set("foo", "bar")
    print conn.get("foo")

The API functions exactly like the normal Connection API, except that the
implementation is significantly different.

Note that the new `GCouchbase` class does *not* use the same implementation
as the experimental support featured in 1.1.0

~~~~~~~~~~~~~~
Other Examples
~~~~~~~~~~~~~~

There are other examples in the `examples` directory.

---------------------
Building documentaion
---------------------


The documentation is using Sphinx and also needs the numpydoc Sphinx extension.
To build the documentation, go into the `docs` directory and run

.. code-block:: sh

    make html

The HTML output can be found in `docs/build/html/`.

-------
Testing
-------

For running the tests, you need the standard `unittest` module, shipped
with Python. Additionally, the `testresources` package is required.

To run them, use either `py.test`, `unittest` or `trial`.

The tests need a running Couchbase instance. For this, a `tests.ini`
file must be present, containing various connection parameters.
An example of this file may be found in `tests.ini.sample`.
You may copy this file to `tests.ini` and modify the values as needed.

The simplest way to run the tests is to declare a `bucket_prefix` in
the `tests.ini` file and run the `setup_tests.py` script to create
them for you.

.. code-block:: sh

    python setup_tests.py

To run the tests::

    nosetests

-------
Support
-------

If you found an issue, please file it in our JIRA_. You may also ask in the
`#libcouchbase` IRC channel at freenode_. (which is where the author(s)
of this module may be found).

-------
License
-------

The Couchbase Python SDK is licensed under the Apache License 2.0.

.. _Couchbase: http://couchbase.com
.. _libcouchbase: http://couchbase.com/develop/c/current
.. _JIRA: http://couchbase.com/issues/browse/pycbc
.. _freenode: http://freenode.net/irc_servers.shtml
