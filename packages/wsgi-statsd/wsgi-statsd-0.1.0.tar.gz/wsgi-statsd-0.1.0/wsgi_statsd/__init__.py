"""StatsdTimingMiddleware object."""
import re
import time

__version__ = '0.1.0'


class StatsdTimingMiddleware(object):

    """The Statsd timing middleware."""

    def __init__(self, app, client):
        """Initialize the middleware with an application and a Statsd client.

        :param app: The application object.
        :param client: `statsd.StatsClient` object.
        """
        self.app = app
        self.statsd_client = client

    def __call__(self, environ, start_response):
        """Call the application and time it.

        :param environ: Dictionary object, containing CGI-style environment variables.
        :param start_response: Callable used to begin the HTTP response.
        """
        interception = {}

        def start_response_wrapper(status, response_headers, exc_info=None):
            """Closure function to wrap the start_response in order to retrieve the status code which we need to
            generate the key name."""
            interception['status'] = status
            return start_response(status, response_headers, exc_info)

        # Time the call.
        start = time.time()
        result = self.app(environ, start_response_wrapper)
        stop = time.time()

        # Now we can generate the key name.
        status = interception['status'].split()[0]  # Leave only the status code.
        key_name = '.'.join([environ['PATH_INFO'], environ['REQUEST_METHOD'], status])

        # Create the timer object and send the data to statsd.
        timer = self.statsd_client.timer(key_name)
        time_delta = stop - start
        timer.ms = int(round(1000 * time_delta))  # Convert to milliseconds.
        timer.send()

        return result
