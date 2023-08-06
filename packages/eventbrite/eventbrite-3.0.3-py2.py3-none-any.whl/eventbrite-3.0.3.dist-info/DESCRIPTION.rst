===============================
eventbrite-sdk-python
===============================

.. image:: https://badge.fury.io/py/eventbrite.png
    :target: http://badge.fury.io/py/eventbrite

.. image:: https://travis-ci.org/eventbrite/eventbrite-sdk-python.svg?branch=master
        :target: https://travis-ci.org/eventbrite/eventbrite-sdk-python

.. image:: https://pypip.in/d/eventbrite/badge.png
        :target: https://pypi.python.org/pypi/eventbrite


* Official Eventbrite_ SDK for Python
* Free software: Apache 2 license
* Full Documentation: http://eventbrite-sdk-python.readthedocs.org/
* API Reference: https://developer.eventbrite.com/docs/

Installation from PyPI
----------------------

::

    $ pip install eventbrite

If you need to, you can also use `easy_install`::

    $ easy_install eventbrite

Usage
--------

The Eventbrite Python SDK makes it trivial to interact with the Eventbrite API:

.. code-block:: python

    >>> from eventbrite import Eventbrite
    >>> eventbrite = Eventbrite('my-oauth-token')
    >>> user = eventbrite.get_user()  # Not passing an argument returns yourself
    >>> user['id']
    1234567890
    >>> user['name']
    Daniel Roy Greenfeld

You can also specify API endpoints manually:

.. code-block:: python

    >>> user = eventbrite.get('/users/me')
    >>> user['id']
    1234567890
    >>> user['name']
    Daniel Roy Greenfeld

Usage with Frameworks
----------------------

When using Flask, you can convert incoming webhook requests into Eventbrite
API objects using the `webhook_to_object()` method:

.. code-block:: python

    @app.route('/webhook', methods=['POST'])
    def webhook():


        # Use the API client to convert from a webhook to an API object
        api_object = eventbrite.webhook_to_object(request)

        # Process the API object
        if api_object.type == 'User':
            do_user_process(api_object)

        if api_object.type == 'Event':
            do_event_process(api_object)

        return ""

Versioning
----------

Because this client interacts with Eventbrite's third API (a.k.a. APIv3), we are tying our release numbers against it in a modified-semantic system:

* 3.x.x where '3' matches the API version. This will not change until Eventbrite releases a new API version.
* * x.0.x where '0' is increased any time there is a significant change to the API that possibly breaks backwards compatibility
* x.x.1 where '1' is increased on any release that does not break backwards comptability (small, new features, enhancements, bugfixes)

.. _requests: https://pypi.python.org/pypi/requests
.. _Eventbrite: https://www.eventbrite.com




History
-------

3.0.3 (2014-03-02)
------------------

* Fixed import issue with ``__version__``. Thank you @meshy  and @longjos for identifying the problem.

3.0.2 (2014-01-30)
------------------

* Event creation now working.
* Added feature allowing the use of Eventbrite API url at test servers. Should expedite development of tricky post actions.


3.0.1 (2014-01-30)
------------------

* Added reverse mapping for ``get_event_ticket_class()`` method.
* Added ``events`` mapping to provide GET access to the Event endpoint.
* Removed several deprecated JSON mappings.

3.0.0 (2014-01-28)
------------------

* Initial release of 3.0.0 client

3.0.0-alpha (2014-12-05)
------------------------


* Inception


