"""Interceptors for httplib, urllib, urllib2, urllib3 and requests.

"""

from appdynamics.agent.core.correlation import make_header
from appdynamics.agent.interceptor.base import ExitCallInterceptor
from appdynamics.agent.models.exitcalls import EXIT_HTTP


class HTTPConnectionInterceptor(ExitCallInterceptor):
    """Base class for http interceptors.

    Required properties for `get_backend`
    -------------------------------------
        host - the host portion of the URL.
        port - the port portion of the URL.
        scheme - the scheme portion of the URL e.g. 'https'.

    """

    https_base_classes = set()

    def _request_is_https(self, connection):

        if connection.port == 443:
            return True
        return connection.__class__ in self.https_base_classes

    def create_correlation_header(self):
        return make_header(self.agent, self.bt, self.exit_call)

    def add_header(self, header):
        # We can't add the correlation header until after thre request has started, so store it and add it later.
        self['header'] = header

    def get_backend(self):
        host, port, scheme = str(self['host']).encode('utf-8'), self['port'], self['scheme']
        identifying_properties = {
            'Host': host,
            'Port': port,
        }
        display_name = "{scheme}://{host}:{port}".format(scheme=scheme, host=host, port=port)
        return self.agent.backend_registry.get_backend(EXIT_HTTP, identifying_properties, display_name)

    def _putrequest(self, putrequest, connection, method, url, *args, **kwargs):
        with self.log_exceptions():
            self['host'] = connection.host
            self['port'] = connection.port
            if self._request_is_https(connection):
                self['scheme'] = 'https'
            else:
                self['scheme'] = 'http'

            self.start_exit_call(operation=url)
        return putrequest(connection, method, url, *args, **kwargs)

    def _endheaders(self, endheaders, connection, *args, **kwargs):
        with self.log_exceptions():
            header = self['header']
            if header:
                connection.putheader(*header)
        return endheaders(connection, *args, **kwargs)

    def _getresponse(self, getresponse, connection, *args, **kwargs):
        # CORE-40945 Catch TypeError as a special case for Python 2.6 and call getresponse with just the
        # HTTPConnection instance.
        try:
            with self.call_and_reraise_on_exception(self.end_exit_call, ignored_exceptions=(TypeError,)):
                response = getresponse(connection, *args, **kwargs)
        except TypeError:
            with self.call_and_reraise_on_exception(self.end_exit_call):
                response = getresponse(connection)

        self.end_exit_call()
        return response


def intercept_httplib(agent, mod):
    interceptor = HTTPConnectionInterceptor(agent, mod.HTTPConnection)
    interceptor.attach(['putrequest', 'endheaders'])

    # CORE-40945 Do not wrap getresponse in the default wrapper.
    interceptor.attach('getresponse', wrapper_func=None)
    HTTPConnectionInterceptor.https_base_classes.add(mod.HTTPSConnection)


def intercept_urllib3(agent, mod):
    # urllib3 1.8+ provides its own HTTPSConnection class, so we need to add it to our list of base classes.
    if hasattr(mod, 'connection'):
        HTTPConnectionInterceptor.https_base_classes.add(mod.connection.HTTPSConnection)


def intercept_requests(agent, mod):
    # requests ships with its own version of urllib3, so we need to manually intercept it.
    intercept_urllib3(agent, mod.packages.urllib3)


def intercept_boto(agent, mod):
    HTTPConnectionInterceptor.https_base_classes.add(mod.CertValidatingHTTPSConnection)
