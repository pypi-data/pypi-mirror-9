"""StatsdTimingMiddleware object."""
import time

__version__ = '0.2.4'

import re

CHAR_RE = re.compile(r'[^\w]')


class StatsdTimingMiddleware(object):

    """The Statsd timing middleware."""

    def __init__(self, app, client, time_exceptions=False, separator='_'):
        """Initialize the middleware with an application and a Statsd client.

        :param app: The application object.
        :param client: `statsd.StatsClient` object.
        :param time_exceptions: send stats when exception happens or not, `False` by default.
        :type time_exceptions: bool
        :param separator: separator of the parts of key sent to statsd, defaults to '_'
        :type separator: str
        """
        self.app = app
        self.statsd_client = client
        self.time_exceptions = time_exceptions
        self.separator = separator

    def __call__(self, environ, start_response):
        """Call the application and time it.

        :param environ: Dictionary object, containing CGI-style environment variables.
        :param start_response: Callable used to begin the HTTP response.
        """
        response_interception = {}

        def start_response_wrapper(status, response_headers, exc_info=None):
            """Wrap the start_response in order to retrieve the status code."""
            response_interception.update(status=status, response_headers=response_headers, exc_info=exc_info)
            return start_response(status, response_headers, exc_info)

        # Time the call.
        start = time.time()
        try:
            response = self.app(environ, start_response_wrapper)
            try:
                for event in response:
                    yield event
            finally:
                if hasattr(response, 'close'):
                    response.close()
            self.send_stats(start, environ, response_interception)
        except Exception as exception:
            if self.time_exceptions:
                self.send_stats(start, environ, response_interception, exception)
            raise

    def get_key_name(self, environ, response_interception, exception=None):
        """Get the timer key name.

        :param environ: wsgi environment
        :type environ: dict
        :param response_interception: dictionary in form
            {'status': '<response status>', 'response_headers': [<response headers], 'exc_info': <exc_info>}
            This is the interception of what was passed to start_response handler.
        :type response_interception: dict
        :param exception: optional exception happened during the iteration of the response
        :type exception: Exception

        :return: string in form '{{PATH}}_{{METHOD}}_{{STATUS_CODE}}'
        :rtype: str
        """
        status = response_interception.get('status')
        status_code = status.split()[0]  # Leave only the status code.
        # PATH_INFO can be empty, so falling back to '/' in that case
        path = CHAR_RE.sub(self.separator, (environ['PATH_INFO'] or '/')[1:])
        parts = [path, environ['REQUEST_METHOD'], status_code]
        if exception:
            parts.append(exception.__class__.__name__)
        return self.separator.join(parts)

    def send_stats(self, start, environ, response_interception, exception=None):
        """Send the actual timing stats.

        :param start: start time in seconds since the epoch as a floating point number
        :type start: float
        :param environ: wsgi environment
        :type environ: dict
        :param response_interception: dictionary in form
            {'status': '<response status>', 'response_headers': [<response headers], 'exc_info': <exc_info>}
            This is the interception of what was passed to start_response handler.
        :type response_interception: dict
        :param exception: optional exception happened during the iteration of the response
        :type exception: Exception
        """
        # It could happen that start_response wasn't called or it failed, so we might have an empty interception
        if response_interception:
            # Create the timer object and send the data to statsd.
            key_name = self.get_key_name(environ, response_interception, exception=exception)
            timer = self.statsd_client.timer(key_name)
            timer._start_time = start
            timer.stop()
