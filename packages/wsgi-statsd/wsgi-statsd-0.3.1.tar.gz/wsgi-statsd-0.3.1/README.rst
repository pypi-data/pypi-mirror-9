wsgi-statsd documentation
=========================

.. image:: https://api.travis-ci.org/paylogic/wsgi-statsd.png
   :target: https://travis-ci.org/paylogic/wsgi-statsd

.. image:: https://pypip.in/v/wsgi-statsd/badge.png
   :target: https://crate.io/packages/wsgi-statsd/

.. image:: https://coveralls.io/repos/paylogic/wsgi-statsd/badge.svg?branch=master
    :target: https://coveralls.io/r/paylogic/wsgi-statsd?branch=master

.. image:: https://readthedocs.org/projects/wsgi-statsd/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/wsgi-statsd/

wsgi_statsd is a WSGI middleware that provides an easy way to time all requests.
Integration is as easy as just wrapping your existing wsgi application.

.. contents::


Usage
-----

In your wsgi.py file wrap your WSGI application as follows:

.. code-block:: python

    import statsd
    from wsgi_statsd import StatsdTimingMiddleware


    def application(environ, start_response):
        response_body = 'The request method was %s' % environ['REQUEST_METHOD']
        status = '200 OK'
        response_headers = [('Content-Type', 'text/plain'),
                            ('Content-Length', str(len(response_body)))]

        start_response(status, response_headers)

        return [response_body]

    client = statsd.StatsClient(
        prefix='your_prefix',
        host='your_host',
        port=8125
    )

    application = StatsdTimingMiddleware(application, client)

.. note::

    If an unhandled exception happens, it will not be timed by default.
    This is a design decision to separate error reporting and actual statistical measurements.
    To enable exception timing, pass `time_exception=True` to the middleware constructor:


.. code-block:: python

    application = StatsdTimingMiddleware(application, client, time_exceptions=True)


What it does
------------

wsgi-statsd uses the statsd timer function, generates a key and sets the amount of time the request took as the value.
The key is constructed as follows:

``<statsd-client-prefix>.<separator-joined-path>.<request-method>.<response-code>.<exception-name>``

Using the ``foo`` prefix, in your statsd client, and calling the ``www.spam.com/bar/test/`` page will result in ``foo
.bar_test.GET.200`` having a value equal to the time it took to handle the request.

If you passed `time_exceptions=True` and any exception occurs during the response, then the key name will be postfixed
with the exception class name: ``foo.bar_test.GET.500.ValueError``.


Customizing for your needs
--------------------------

It's possible to customize the way ``wsgi_statsd`` generates the key and/or time. ``StatsdTimingMiddleware`` has
``send_stats`` and ``get_key_name`` which you can override:

.. code-block:: python

    class CustomStatsdMiddleware(StatsdTimingMiddleware):

        def get_key_name(self, environ, response_interception):
            return super(self, CustomStatsdMiddleware).get_key_name(environ, response_interception) + '.' + environ['Transfer-Encoding']


        def send_stats(self, start, environ, response_interception):
            super(self, CustomStatsdMiddleware).send_stats(start + 10, environ, response_interception)


wsgi-statsd uses underscores as a separator for the path part of the key that is sent to statsd as that makes it
easy to retrieve the data from graphite. You can override this default by passing a ``separator`` value to the
middleware constructor:


.. code-block:: python

    StatsdTimingMiddleware(application, client, separator='.')


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/wsgi-statsd>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_.

Please refer to the `license file <https://github.com/paylogic/wsgi-statsd/blob/master/LICENSE.txt>`_.


© 2015 Wouter Lansu, Paylogic International and others.
