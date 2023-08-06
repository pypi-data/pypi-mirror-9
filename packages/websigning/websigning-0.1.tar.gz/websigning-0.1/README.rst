Documentation
=============

See https://wiki.mozilla.org/Apps/WebApplicationReceipt/SigningService


Dev and testing
---------------

Create a virtualenv of your choosing and activate it::

    virtualenv websigning
    source websigning/bin/activate

Or using virtualenvwrapper::

    mkvirtualenv websigning


Install the dependencies::

    python setup.py develop


Run tests::

    python setup.py nosetests


When testing, you may see output along the lines of:

   "InsecurePlatformWarning: A true SSLContext object is not available."

This seems to be a feature of newer versions of the request module.  This can be solved by installing by running:

    pip install requests[security]
