=================================================================
sqlitedict -- persistent ``dict``, backed-up by SQLite and pickle
=================================================================

|Travis|_
|Downloads|_
|License|_

.. |Travis| image:: https://api.travis-ci.org/piskvorky/sqlitedict.png?branch=master
.. |Downloads| image:: https://pypip.in/d/sqlitedict/badge.png
.. |License| image:: https://pypip.in/license/sqlitedict/badge.png
.. _Travis: https://travis-ci.org/piskvorky/sqlitedict
.. _Downloads: https://pypi.python.org/pypi/sqlitedict
.. _License: https://pypi.python.org/pypi/sqlitedict

A lightweight wrapper around Python's sqlite3 database, with a dict-like interface
and multi-thread access support:

.. code-block:: python

  >>> mydict = SqliteDict('some.db', autocommit=True) # the mapping will be persisted to file `some.db`
  >>> mydict['some_key'] = any_picklable_object
  >>> print mydict['some_key']
  >>> print len(mydict) # etc... all dict functions work

Pickle is used internally to (de)serialize the values. Keys are strings.

If you don't use autocommit (default is no autocommit for performance), then
don't forget to call ``mydict.commit()`` when done with a transaction.

Features
--------

* Values can be **any picklable objects** (uses ``cPickle`` with the highest protocol).
* Support for **multiple tables** (=dicts) living in the same database file.
* Support for **access from multiple threads** to the same connection (needed by e.g. Pyro).
  Vanilla sqlite3 gives you ``ProgrammingError: SQLite objects created in a thread can
  only be used in that same thread.``

Concurrent requests are still serialized internally, so this "multithreaded support"
**doesn't** give you any performance benefits. It is a work-around for sqlite limitations in Python.

Installation
------------

The module has no dependencies beyond Python itself. The minimum Python version is 2.5, continuously tested on Python 2.6, 2.7, 3.3 and 3.4 `on Travis <https://travis-ci.org/piskvorky/sqlitedict>`_.

Install or upgrade with::

    easy_install -U sqlitedict

or from the `source tar.gz <http://pypi.python.org/pypi/sqlitedict>`_::

    python setup.py install

Documentation
-------------

Standard Python document strings are inside the module:

.. code-block:: python

  >>> import sqlitedict
  >>> help(sqlitedict)

(but it's just ``dict`` with a commit, really).

**Beware**: because of Python semantics, ``sqlitedict`` cannot know when a mutable persistent-dictionary entry was modified.
For example, ``mydict.setdefault('new_key', []).append(1)`` will leave ``mydict['new_key']`` equal to empty list, not ``[1]``.
You'll need to explicitly assign the mutated object back to achieve the same effect:

.. code-block:: python

  >>> val = mydict.get('new_key', [])
  >>> val.append(1)
  >>> mydict['new_key'] = val


For developers
--------------

Install::

    # pip install nose
    # pip install coverage

To perform all tests::

   # make test-all

To perform all tests with coverage::

   # make test-all-with-coverage


Comments, bug reports
---------------------

``sqlitedict`` resides on `github <https://github.com/piskvorky/sqlitedict>`_. You can file
issues or pull requests there.

----

``sqlitedict`` is open source software released under the `Apache 2.0 license <http://opensource.org/licenses/apache2.0.php>`_.
Copyright (c) 2011-now Radim Rehurek and authors.
