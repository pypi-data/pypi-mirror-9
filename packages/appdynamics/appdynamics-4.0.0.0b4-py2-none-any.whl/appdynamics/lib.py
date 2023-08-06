"""Utilities for AppDynamics Python code.

"""

from collections import Mapping
import os
import random
import sys
import time
from uuid import uuid4
import wsgiref.util
from logging import Formatter
from appdynamics_bindeps.google.protobuf.descriptor import FieldDescriptor

default_log_formatter = Formatter('%(asctime)s [%(levelname)s] %(name)s <%(process)d>: %(message)s')

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY3:
    b = lambda x: x.encode('ISO-8859-1')
    u = lambda x: x
    b2u = lambda x: x.decode('ISO-8859-1')
    u2b = lambda x: x.encode('ISO-8859-1')

    xrange = range

    iterkeys = lambda m: iter(m.keys())
    itervalues = lambda m: iter(m.values())
    iteritems = lambda m: iter(m.items())

    keys = lambda m: list(m.keys())
    values = lambda m: list(m.values())
    items = lambda m: list(m.items())
else:
    import codecs

    b = lambda x: x
    u = lambda x: codecs.unicode_escape_decode(x)[0]
    b2u = lambda x: u(x)
    u2b = lambda x: x.encode('ISO-8859-1')

    iterkeys = lambda m: m.iterkeys()
    itervalues = lambda m: m.itervalues()
    iteritems = lambda m: m.iteritems()

    keys = lambda m: m.keys()
    values = lambda m: m.values()
    items = lambda m: m.items()


try:
    from urllib.parse import parse_qs, parse_qsl
except ImportError:
    from urlparse import parse_qs, parse_qsl

try:
    from urllib.parse import urlparse as parse_url
except ImportError:
    from urlparse import urlparse as parse_url

try:
    from http.cookie import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie

try:
    import greenlet
    get_ident = lambda: hash(greenlet.getcurrent())
    GREENLETS_ENABLED = True
except ImportError:
    GREENLETS_ENABLED = False
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class Counter(dict):
    """A minimal version of collections.Counter.

    Counter was added in Python 2.7. Its implementation is no
    more efficient than this, so we may as well just use our
    own minimalist version always.

    """
    def __init__(self, iterable=None, **kwargs):
        super(Counter, self).__init__()
        self.update(iterable, **kwargs)

    def update(self, iterable=None, **kwargs):
        if iterable is not None:
            _get = self.get
            if isinstance(iterable, Mapping):
                if not self:
                    super(Counter, self).update(iterable)
                else:
                    for k, count in iterable.iteritems():
                        self[k] = _get(k, 0) + count
            else:
                for elt in iterable:
                    self[elt] = _get(elt, 0) + 1
        if kwargs:
            self.update(kwargs)

    def __missing__(self, key):
        return 0


def make_uuid():
    return uuid4().hex


_RNG = random.Random()
_RNG.seed(os.getpid() ^ int(time.time()))
_MAX_REQUEST_ID = 2**63 - 1


def make_random_id():
    random_id = _RNG.randint(1, _MAX_REQUEST_ID)
    return random_id


def search(pred, items, default=None):
    for item in items:
        if pred(item):
            return item
    return default


def set_fields(obj, **kwargs):
    for k, v in iteritems(kwargs):
        setattr(obj, k, v)
    return obj


def getenv(envkey, default, mapper=None):
    value = os.getenv(envkey, default)

    if mapper and value is not None:
        try:
            value = mapper(value)
        except:
            value = default

    return value


class LazyWsgiRequest(object):
    """Lazily read request line and headers from a WSGI environ.

    This matches enough of the Werkzeug Request API for the agent's needs: it
    only provides access to the information in the request line and the
    headers that is needed for the agent. (Since the agent doesn't inspect
    the request body, we don't touch any of that.)

    Parameters
    ----------
    environ : dict
        A WSGI environment.

    Attributes
    ----------
    headers : dict
        A dictionary of the HTTP headers. The headers are lowercase with
        dashes separating words.
    method : str
        The request method (e.g., GET).
    url : str
        The URL of the request (reconstructed according to PEP 333).
    cookies : dict
        The cookies passed in the request header (if any).
    path : str
        The path part of the request. Note that unlike raw WSGI, this will be
        just '/' if it would otherwise be empty.
    args : dict
        The query parameters. This is not a multi-dict: if a parameter is
        repeated multiple times, one of them wins.

    """
    DEFAULT_PORTS = {
        'http': 80,
        'https': 443,
    }

    def __init__(self, environ):
        super(LazyWsgiRequest, self).__init__()
        self.environ = environ.copy()

        self._headers = None
        self._host = None
        self._port = None
        self._http_host = None
        self._url = None
        self._path = None
        self._args = None
        self._cookies = None

    @property
    def headers(self):
        if self._headers is not None:
            return self._headers

        headers = {}
        for key, value in iteritems(self.environ):
            if key.startswith('HTTP_'):
                header_name = key[5:].lower().replace('_', '-')
                headers[header_name] = value

        self._headers = headers
        return headers

    @property
    def method(self):
        return self.environ['REQUEST_METHOD']

    @property
    def is_secure(self):
        return self.environ['wsgi.url_scheme'] == 'https'

    @property
    def host(self):
        if self._host is None:
            host = self.environ.get('HTTP_X_FORWARDED_HOST')

            if host:
                self._host = host.split(',')[0].strip()
            else:
                self._host = self.environ.get('HTTP_HOST')

            if self._host is None:
                host = self.environ['SERVER_NAME']
                port = str(self.environ['SERVER_PORT'])

                if (self.environ['wsgi.url_scheme'], port) not in (('http', '80'), ('https', '443')):
                    self._host = '%s:%s' % (host, port)
                else:
                    self._host = host

        return self._host

    @property
    def url(self):
        if self._url is None:
            self._url = wsgiref.util.request_uri(self.environ)
        return self._url

    @property
    def cookies(self):
        if self._cookies is not None:
            return self._cookies

        cookies = {}
        cookie_header = self.environ.get('HTTP_COOKIE', None)

        if cookie_header:
            cookie_jar = SimpleCookie()

            try:
                cookie_jar.load(cookie_header)
            except:
                self._cookies = {}
                return self._cookies

            for name in cookie_jar:
                cookies[name] = cookie_jar[name].value

        self._cookies = cookies
        return cookies

    @property
    def path(self):
        if self._path is not None:
            return self._path

        self._path = self.environ.get('PATH_INFO') or '/'
        return self._path

    @property
    def args(self):
        if self._args is not None:
            return self._args

        query_string = self.environ.get('QUERY_STRING', '')
        self._args = dict((k, v) for k, v in parse_qsl(query_string))
        return self._args


def get_request_host_and_port(request):
    """Return a tuple of the host and port from an incoming HTTP request.

    Parameters
    ----------
    request : request-like object
        The request must have `environ` and `host` attributes with the same
        meaning as those attributes in Werkzeug's BaseRequest class.

    Returns
    -------
    (host, port)
        The host and the port. The port is set even if it's the default for
        requests of this scheme.

    """
    host = request.host
    port = None

    if ':' in host:
        host, port = host.split(':', 1)

    return host, (port or request.environ['SERVER_PORT'])


def running_tests():
    return (hasattr(sys, 'argv') and any(x for x in sys.argv if 'nosetests' in x))


def internal_frame(fn):
    return 'site-packages/appdynamics' in fn


def make_name_value_pairs(*dicts):
    """Convert dicts into a list of name value pairs for use in a 'Common.NameValuePair' protobuf field.

    """

    result = []
    for item in dicts:
        result.extend([
            dict(name=str(k), value=str(v))
            for k, v in iteritems(item)
        ])
    return result


def merge_protobuf(existing_pb, incoming_pb):
    """Merge an incoming protobuf message into an existing protobuf.

    We need to remove any updated repeated fields from the existing_pb first
    because MergeFrom will simply append them.

    """
    def remove_repeated_fields(existing_pb, incoming_pb):
        for k, v in incoming_pb.ListFields():
            if k.label == FieldDescriptor.LABEL_REPEATED:
                existing_pb.ClearField(k.name)
            elif k.type == FieldDescriptor.TYPE_MESSAGE and existing_pb.HasField(k.name):
                    remove_repeated_fields(getattr(existing_pb, k.name), v)

    remove_repeated_fields(existing_pb, incoming_pb)
    return existing_pb.MergeFrom(incoming_pb)
