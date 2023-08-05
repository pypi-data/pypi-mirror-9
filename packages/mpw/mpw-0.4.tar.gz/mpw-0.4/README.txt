Master Password
===============

This is a Python implementation of the `Master Password algorithm`__ by
`Maarten Billemont`__. It also comes with a command line interface that lets
you compute passwords for your sites based on your master password.

__ http://masterpasswordapp.com/algorithm.html
__ http://lhunath.com


Installation
------------

This package requires Python 3 (tested with 3.4) and uses scrypt__,
cryptography__ (you need a compiler for both),  click__, and pyperclip__.

Installation with `pip`__:

.. code-block:: bash

   $ pip install mpw

Or better, use `pipsi`__:

.. code-block:: bash

   $ pipsi install --python `which python3` mpw

This app copies the password to the clipboard. This should work out-of-the-box
on OS X and Windows. On Linux, *mpw* makes use of the ``xclip`` or ``xsel`` commands, which should come with the os. Otherwise run:

.. code-block:: bash

   $ sudo apt-get install xclip
   $ # or
   $ sudo apt-get install xsel

Alternatively, the gtk or PyQT4 modules can be installed.

Binary executables (e.g., an installer for Windows) may follow.

__ https://pypi.python.org/pypi/scrypt
__ https://pypi.python.org/pypi/cryptography
__ https://pypi.python.org/pypi/click
__ https://pypi.python.org/pypi/pyperclip
__ https://pypi.python.org/pypi/pip
__ https://github.com/mitsuhiko/pipsi


Usage
-----

.. code-block:: bash

   $ # Add a user
   $ mpw adduser Alice
   Enter master password:
   Confirm master password:
   Added user "Alice".
   # Add a site for Alice
   $ mpw addsite test-site
   Enter master password for "Alice":
   Added site "test-site" for user "Alice".
   $ # Actually get the password
   $ mpw get test-site
   Enter master password for "Alice":
   Password for "test-site" for user "Alice" was copied to the clipboard.
   $ # You can also pipe a password to other commands:
   $ mpw get -e server-root | sudo -S vim /etc/crontab


For more information take a look at the help:

.. code-block:: bash

   $ mpw --help
