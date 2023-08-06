.. _quickstart:

Quick-start
===========

First you instantiate an :py:class:`UnQLite` object, passing in either the path to the database file or the special string ``':mem:'`` for an in-memory database.

Below is a sample interactive console session designed to show some of the basic features and functionality of the unqlite-python library. Also check out the `full API documentation <http://unqlite-python.readthedocs.org/en/latest/api.html>`_.

To begin, instantiate an :py:class:`UnQLite` object. You can specify either the path to a database file, or use UnQLite as an in-memory database.

.. code-block:: pycon

    >>> from unqlite import UnQLite
    >>> db = UnQLite()  # Create an in-memory database.

Key/value features
------------------

UnQLite can be used as a key/value store.

.. code-block:: pycon

    >>> db['foo'] = 'bar'  # Use as a key/value store.
    >>> print db['foo']
    bar

    >>> for i in range(4):
    ...     db['k%s' % i] = str(i)
    ...

    >>> 'k3' in db
    True
    >>> 'k4' in db
    False
    >>> del db['k3']

    >>> db.append('k2', 'XXXX')
    >>> db['k2']
    '2XXXX'

The database can also be iterated in key-order:

.. code-block:: pycon

    >>> [item for item in db]
    [('foo', 'bar'), ('k0', '0'), ('k1', '1'), ('k2', '2XXXX')]

Cursors
-------

For finer-grained record traversal, you can use cursors.

.. code-block:: pycon

    >>> with db.cursor() as cursor:
    ...     cursor.seek('k0')
    ...     for key, value in cursor:
    ...         print key, '=>', value
    ...
    k0 => 0
    k1 => 1
    k2 => 2XXXX

Cursors also support a couple shortcut methods to simplify common iteration patterns:

.. code-block:: pycon

    >>> with db.cursor() as cursor:
    ...     list(cursor.fetch_count(3))
    ...
    [('foo', 'bar'), ('k0', '0'), ('k1', '1')]

    >>> with db.cursor() as cursor:
    ...     cursor.seek('k0')
    ...     list(cursor.fetch_until('k2', include_stop_key=False))
    ...
    [('k0', '0'), ('k1', '1')]

For more information, see the :py:class:`Cursor` API documentation.

Document store features
-----------------------

In my opinion the most interesting feature of UnQLite is its JSON document store. The `Jx9 scripting language <http://unqlite.org/jx9.html>`_ is used to interact with the document store, and it is a wacky mix of C, JavaScript and maybe even PHP.

Interacting with the document store basically consists of creating a Jx9 script (you might think of it as an imperative SQL query), compiling it, and then executing it.

.. code-block:: pycon

    >>> script = """
    ...     db_create('users');
    ...     db_store('users', $list_of_users);
    ...     $users_from_db = db_fetch_all('users');
    ... """

    >>> list_of_users = [
    ...     {'username': 'Huey', 'age': 3},
    ...     {'username': 'Mickey', 'age': 5}
    ... ]

    >>> with db.compile_script(script) as vm:
    ...     vm['list_of_users'] = list_of_users
    ...     vm.execute()
    ...     users_from_db = vm['users_from_db']
    ...
    True

    >>> users_from_db  # UnQLite assigns items in a collection an ID.
    [{'username': 'Huey', 'age': 3, '__id': 0},
     {'username': 'Mickey', 'age': 5, '__id': 1}]

This is just a taste of what is possible with Jx9. In the near future I may add some wrappers around common Jx9 collection operations, but for now hopefully it is not too difficult to work with.

More information can be found in the :py:class:`VM` documentation.

Collections
-----------

To simplify working with JSON document collections, ``unqlite-python`` provides a light API for
executing Jx9 queries on collections. A collection is an ordered list of JSON objects
(records). Records can be appended or deleted, and in the next major release of UnQLite there will
be support for updates as well.

To begin working with :py:class:`Collection`, you can use the :py:meth:`UnQLite.collection` factory method:

.. code-block:: pycon

    >>> users = db.collection('users')
    >>> users.create()  # Create the collection if it does not exist.
    >>> users.exists()
    True

You can use the :py:meth:`Collection.store` method to add one or many records. To add a single record just pass in a python ``dict``. To add multiple records, pass in a list of dicts. Records can be fetched and deleted by ID using :py:meth:`~Collection.fetch` and :py:meth:`~Collection.delete`.

.. code-block:: pycon

    >>> users.store([
    ...     {'name': 'Charlie', 'color': 'green'},
    ...     {'name': 'Huey', 'color': 'white'},
    ...     {'name': 'Mickey', 'color': 'black'}])
    True
    >>> users.store({'name': 'Leslie', 'color': 'also green'})
    True

    >>> users.fetch(0)  # Fetch the first record.
    {'__id': 0, 'color': 'green', 'name': 'Charlie'}

    >>> users.delete(0)  # Delete the first record.
    True
    >>> users.delete(users.last_record_id())  # Delete the last record.
    True

You can retrieve all records in the collection, or specify a filtering function. The filtering function will be registered as a foreign function with the Jx9 VM and called *from* the VM.

.. code-block:: pycon

    >>> users.all()
    [{'__id': 1, 'color': 'white', 'name': 'Huey'},
     {'__id': 2, 'color': 'black', 'name': 'Mickey'}]

    >>> users.filter(lambda obj: obj['name'].startswith('H'))
    [{'__id': 1, 'color': 'white', 'name': 'Huey'}]

More information can be found in the :py:class:`Collection` documentation.

Transactions
------------

UnQLite supports transactions for file-backed databases (since transactions occur at the filesystem level, they have no effect on in-memory databases).

The easiest way to create a transaction is with the context manager:

.. code-block:: pycon

    >>> db = UnQLite('/tmp/test.db')
    >>> with db.transaction():
    ...     db['k1'] = 'v1'
    ...     db['k2'] = 'v2'
    ...
    >>> db['k1']
    'v1'

You can also use the transaction decorator which will wrap a function call in a transaction and commit upon successful execution (rolling back if an exception occurs).

.. code-block:: pycon

    >>> @db.commit_on_success
    ... def save_value(key, value, exc=False):
    ...     db[key] = value
    ...     if exc:
    ...         raise Exception('uh-oh')
    ...
    >>> save_value('k3', 'v3')
    >>> save_value('k3', 'vx', True)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "unqlite/core.py", line 312, in wrapper
        return fn(*args, **kwargs)
      File "<stdin>", line 5, in save_value
    Exception: uh-oh
    >>> db['k3']
    'v3'

For finer-grained control you can call :py:meth:`~UnQLite.begin`, :py:meth:`~UnQLite.rollback` and :py:meth:`~UnQLite.commit` manually.

.. code-block:: pycon

    >>> db.begin()
    >>> db['k3'] = 'v3-xx'
    >>> db.commit()
    True
    >>> db['k3']
    'v3-xx'
