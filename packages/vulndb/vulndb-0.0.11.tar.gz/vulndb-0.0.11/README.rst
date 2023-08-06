Python SDK to access the `vulnerability database <https://github.com/vulndb/data>`_

.. image:: https://circleci.com/gh/vulndb/python-sdk/tree/master.svg?style=svg
   :alt: Build Status
   :align: right
   :target: https://circleci.com/gh/vulndb/python-sdk/tree/master

Installation
============
It's possible to install `the latest stable release from pypi <https://pypi.python.org/pypi/vulndb>`_:

::

    pip install vulndb


Or if you're interested in the latest version from our repository:

::

    git clone https://github.com/vulndb/python-sdk.git
    python setup.py install

Usage
=====

::

    >>> from vulndb import DBVuln
    >>> dbv = DBVuln.from_id(42)
    >>> dbv.title
    'SQL Injection'
    >>> dbv.description
    'A long and actionable description for SQL injection ...'
    >>> dbv.fix_guidance
    'Explains the developer how to fix SQL injections, usually a couple of <p> long ...'
    >>> dbv.severity
    'high'
    >>> r = dbv.references[0]
    >>> r.url
    'http://example.com/sqli-description.html'
    >>> r.title
    'SQL injection cheat-sheet'


More attributes, methods and helpers are well documented and available in the
`source code <https://github.com/vulndb/python-sdk/blob/master/vulndb/db_vuln.py>`_.

Contributing
============
Send your `pull requests <https://help.github.com/articles/using-pull-requests/>`_
with improvements and bug fixes, making sure that all tests ``PASS``:

::

    $ cd python-sdk
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r vulndb/requirements-dev.txt
    $ nosetests vulndb/
    ..........
    ----------------------------------------------------------------------
    Ran 10 tests in 0.355s

    OK


Updating the database
=====================
This package embeds the `vulnerability database <https://github.com/vulndb/data>`_
in the ``vulndb/db/`` directory. To update the database with new information
follow these steps:

::

    # Update the database
    . tools/update-db.sh

After updating the database it's a good idea to publish the latest at ``pypi`` using:

::

    python setup.py sdist upload


