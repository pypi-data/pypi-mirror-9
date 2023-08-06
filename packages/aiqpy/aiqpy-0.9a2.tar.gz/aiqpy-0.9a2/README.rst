aiqpy
=====

aiqpy is a wrapper library that allows you to interact with an `AppearIQ 8 <https://appeariq.com>`_ platform using Python.

The library connects to the REST APIs of the platform and takes care of authentication and session management so you can focus on funnier things.


Example: Changing the password of a user
----------------------------------------
.. code-block:: pycon

    >>> platform = aiqpy.Connection(profile='dev')
    >>> user = platform.get(['admin', 'users'], username='stephen.falken')[0]
    >>> user['password'] = 'joshua'
    >>> updated = platform.put(['admin', 'users'], user)

Dependencies
------------
aiqpy uses `Requests <http://python-requests.org>`_ for performing HTTP requests.

License
-------
aiqpy is licensed under GNU GPL v3.0.
