aiqterminal
===========

aiqterminal is a an interactive shell for administrating an `AppearIQ 8 <https://appeariq.com>`_ platform.


Example: Changing the password of a user
----------------------------------------
.. code-block:: pycon

    admin@wapr/default> set_organization('games')
    admin@wapr/games> user = get(['admin', 'users'], username='stephen.falken')[0]
    admin@wapr/games> user['password'] = 'joshua'
    admin@wapr/games> updated = put(['admin', 'users'], user)

Dependencies
------------
aiqterminal uses `aiqpy <https://pypi.python.org/pypi/aiqpy>`_ for performing HTTP requests.

License
-------
aiqterminal is licensed under GNU GPL v3.0.
