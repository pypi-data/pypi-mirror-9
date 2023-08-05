wsgi-statsd documentation
=========================

.. image:: https://api.travis-ci.org/paylogic/wsgi-statsd.png
   :target: https://travis-ci.org/paylogic/wsgi-statsd

.. image:: https://pypip.in/v/wsgi-statsd/badge.png
   :target: https://crate.io/packages/wsgi-statsd/

.. image:: https://coveralls.io/repos/paylogic/wsgi-statsd/badge.svg?branch=master
    :target: https://coveralls.io/r/paylogic/wsgi-statsd?branch=master

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

What it does
------------

The middleware uses the statsd timer function, using the environ['PATH_INFO'], environ['REQUEST_METHOD'] and
the status code variables as the name for the key and the amount of time the request took as the value.

That's it.

If you want more granular reporting you'll have to work with the ``prefix`` argument. You can pass any string you want
and the middleware will pass it along to statsd.

Using the ``foo`` prefix and calling the ``www.spam.com/bar`` page will result in ``foo.bar.GET.200`` having a value
equal to the time it took to handle the request.


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/wsgi-statsd>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

Please refer to the `license file <https://github.com/paylogic/wsgi-statsd/blob/master/LICENSE.txt>`_


© 2015 Wouter Lansu, Paylogic International and others.
