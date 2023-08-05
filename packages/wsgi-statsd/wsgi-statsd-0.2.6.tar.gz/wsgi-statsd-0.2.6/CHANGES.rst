Changelog
=========

0.2.5
-----

* Fixed issue with the separator parameter. It now functions as expected and documented.

0.2.4
-----

* Add separator parameter to StatsdTimingMiddleware.__init__().

0.2.3
-----

* Add exception class name to the key when exception happens (bubenkoff)

0.2.1
-----

* ensure close() is properly called from the response (bubenkoff, GrahamDumpleton)
* optionally time exceptions (bubenkoff)
* code readability improvements (bubenkoff)

0.2.0
-----

* Fixed version numbers
* Added support for WSGI applications returning generators
* Added a test to verify that the response body remains the same after passing through the middleware

0.1.0
-----

* Initial public release
