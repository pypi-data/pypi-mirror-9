"""Models and mappers for business transactions.

Atttributes
-----------
ENTRY_WSGI : int, const
    A constant representing the WSGI entry point type.
ENTRY_FLASK : int, const
    A constant representing the Flask entry point type.
ENTRY_DJANGO : int, const
    A constant representing the Django entry point type.

Examples
--------
Transactions should be created using a transaction factory. To get a
transaction factory, you first need a timer factory such as the `timer` method
of an `Agent` instance:

    >>> from appdynamics.agent.core import Agent
    >>> agent = Agent()

Once you have the timer factory, create a transaction factory:

    >>> factory = make_transaction_factory(agent.timer)

You can now use `factory` to create transactions:

    >>> bt = factory()

The returned transaction has a timer that has not been started. You can start
the timer by calling `start` on it:

    >>> bt.timer.start()

To conveniently set attributes of the created transaction, pass keyword
arguments to the factory that correspond to the transaction's attributes:

    >>> bt = factory(name='my-custom-bt', registered_id=42)
    >>> bt.name
    'my-custom-bt'
    >>> bt.registered_id
    42

You can, of course, always set an attribute of a BT directly:

    >>> bt.entry_type = ENTRY_FLASK

You can convert transactions into variable dictionaries that can then be
packed into various protobufs:

    >>> bt_identifier = make_bt_identifier_dict(bt)
    {'type': 1, 'btID': 42}
    >>> from appdynamics.agent.pb import pb_from_dict
    >>> pb_from_dict(pb.BTIdentifier(), bt_identifier)

"""

import threading
import weakref
import sys

from appdynamics.lib import make_random_id, GREENLETS_ENABLED, u2b

from appdynamics.agent import pb
from appdynamics.agent.core import correlation, snapshot

from appdynamics.agent.models import callgraph, errors, exitcalls


if GREENLETS_ENABLED:
    import greenlet


ENTRY_PYTHON_WEB = pb.PYTHON_WEB
ENTRY_WSGI = ENTRY_PYTHON_WEB
ENTRY_FLASK = ENTRY_PYTHON_WEB
ENTRY_DJANGO = ENTRY_PYTHON_WEB
ENTRY_CELERY = ENTRY_PYTHON_WEB
ENTRY_CLI = ENTRY_PYTHON_WEB


def make_transaction_factory(timer_factory):
    """Return a factory that creates transactions.

    Parameters
    ----------
    timer_factory : callable
        A callable with no required arguments that returns a timer object
        compatible with `appdynamics.agent.core.timer.Timer`.

    Returns
    -------
    factory : callable
        A callable with no positional arguments that returns a new `Transaction`
        instance when called. Any keyword arguments to this callable are set as
        attributes of the returned transaction.

    """
    def factory(**kwargs):
        bt = Transaction(timer_factory)

        for k, v in kwargs.items():
            setattr(bt, k, v)

        return bt

    return factory


class Transaction(object):
    """A business transaction.

    Parameters
    ----------
    timer_factory : callable
        A callable taking no parameters that returns a new instance of
        :py:class:`appdynamics.agent.core.timer.Timer` when called

    Attributes
    ----------
    lock : threading.Lock
        A lock that used to synchronize access to the BT for the purposes of
        marking it completed and reporting it
    request_id : long
        A random 64-bit identifier for identifying requests concerning this BT.
    timer : appdynamics.agent.core.timer.Timer
        A timer for keeping track of this BT's duration.
    entry_type : int or bytes
        If the BT originates with this application, one of the `ENTRY_xxx`
        constants defined in :py:mod:`appdynamics.agent.models.transactions`.
        Otherwise, a byte-string with the unparsed name of the entry point
        from the originating BT. (You shouldn't try to parse the entry point
        when it's a byte-string. Just pass it on unmodified.)
    name : str
        The name of this BT.
    registered_id : int or None
        If the BT is registered with the controller, the id it is registered
        with by the controller. Otherwise, `None`.
    naming_scheme_type : str or None
        The name of the naming scheme used to generate the BT name, if any.
        TODO: Describe why this can be `None`.
    incoming_correlation : correlation.CorrelationHeader or None
        If we detected that this BT is continuing a BT, the incoming
        correlation header is stored here. Otherwise, the BT originated at
        with this app, and this attribute is `None`.
    is_sent : bool
        True if this transaction's details have been reported. Otherwise,
        false.
    completed : bool
        True if this transaction has completed (i.e., `end_transaction` has
        been called for it), even if the transaction hasn't been sent.
    bt_info_request : dict or None
        A dict representation of the data for a `pb.BTInfoRequest` that was
        sent when transaction service sent the request. If a request has not
        yet been made for this transaction, then `None`.
    bt_info_response : pb.BTInfoResponse or None
        The response received after sending the `bt_info_request` via the
        transaction service. If the response hasn't been received yet, then
        `None`.
    continuing_snapshot_enabled : bool
        True if this BT is a continuing transaction, and the correlation
        header enabled snapshotting.
    errors : list[errors.ErrorInfo]
        A list of error logs that have been recorded during this BT.
    exceptions : list[errors.ExceptionInfo]
        A list of uncaught exceptions that have been recorded during this BT.
    custom_match_id : int or None
        The id of the custom match point that caused this BT to be matched, if
        any. If the BT was auto-discovered, this will be `None`.

    """

    def __init__(self, timer_factory):
        super(Transaction, self).__init__()

        self.lock = threading.Lock()

        self.request_id = make_random_id()
        self._timer_factory = timer_factory
        self.timer = timer_factory()

        self.is_sent = False
        self.is_crossapp = False

        # Identificaiton of the BT.
        self.entry_type = None
        self.name = None
        self.registered_id = None
        self.naming_scheme_type = None
        self.custom_match_id = None
        self.url = None
        self.status_code = None
        self.request = None

        # Correlation
        self._incoming_correlation = None
        self.cross_app_correlation = None

        # Error and exception handling.
        self.has_errors = False
        self.errors = []
        self.exceptions = []
        self._exception_set = set()

        # Snapshotting.
        self.snapshotting = False
        self.snapshot_start_time_ms = None
        self.snapshot_guid = None
        self.snapshot_trigger = None
        self.sample_data = None

        # Exit calls.
        self._exit_call_id = 0
        self._exit_calls = {}
        self._active_exit_call = None
        self._properties = {}

        # Proxy lifecycle stuff.
        self.bt_info_request = None
        self._bt_info_response = None

        # Thread/greenlet context.
        self.thread_id = threading.current_thread().ident

        try:
            import gevent.event
            self._bt_info_response_event = gevent.event.Event()
        except ImportError:
            self._bt_info_response_event = threading.Event()

        if GREENLETS_ENABLED:
            gr = greenlet.getcurrent()
            self.greenlet_ref = weakref.ref(gr)
        else:
            self.greenlet_ref = None

    @property
    def is_auto_discovered(self):
        return self.naming_scheme_type is not None

    @property
    def bt_info_response(self):
        return self._bt_info_response

    @bt_info_response.setter
    def bt_info_response(self, response):
        self._bt_info_response = response
        if response:
            self._bt_info_response_event.set()

    def wait_for_bt_info_response(self, timeout_ms=10):
        """Wait (exactly once) for the BTInfoResponse or timeout.

        Only waits the first time it's called for this BT if there is no
        BTInfoResponse. If the BT already has a response, or if we have
        already waited, immediately returns.

        Other Parameters
        ----------------
        timeout_ms : int (optional)
            The timeout in milliseconds, defaults to 10ms.

        Returns
        -------
        bool
            True if a BTInfoResponse was received within the timeout, else
            False.

        """
        self._bt_info_response_event.wait(timeout=timeout_ms/1000.0)
        self._bt_info_response_event.set()
        return self._bt_info_response is not None

    @property
    def continuing_snapshot_enabled(self):
        return self._incoming_correlation and self._incoming_correlation[correlation.SNAPSHOT_ENABLED_KEY]

    @property
    def completed(self):
        # A transaction is complete if its timer was started and is currently stopped.
        return self.timer.has_stopped

    @property
    def incoming_correlation(self):
        return self._incoming_correlation

    @incoming_correlation.setter
    def incoming_correlation(self, hdr):
        if hdr and not hdr.is_cross_app:
            self.entry_type = hdr[correlation.BT_TYPE_KEY]
            self.name = hdr[correlation.BT_NAME_KEY]

            def to_long(x):
                try:
                    return long(x)
                except (TypeError, ValueError):
                    return None

            self.registered_id = to_long(hdr[correlation.BT_ID_KEY])
            self.naming_scheme_type = hdr[correlation.BT_MATCH_VALUE_KEY]

        self._incoming_correlation = hdr

    def start_exit_call(self, caller, backend, operation=None, params=None, category=None):
        """Mark the start of an exit call and set the active exit call.

        Parameters
        ----------
        caller : frame
            The Python frame that "initiated" this exit call
        backend : appydynamics.agent.models.exitcalls.Backend
            The backend to which the exit call is made
        operation : str, optional
            A string describing the operation that is being performed, such as
            the URL of an HTTP request or a SQL query for a DB
        params : iterable of strs, optional
            An iterable of strings that are parameters passed to the given
            operation, or `None` (the default) if there are no parameters for
            the operation
        category : str, optional
            A category name for grouping exit calls or `None` (the default) if
            the exit calls should not be explicitly grouped by the agent

        Returns
        -------
        exitcalls.ExitCall or None
            The exit call model or `None` if an exit call couldn't be started

        See Also
        --------
        end_exit_call

        """
        if self._active_exit_call:
            return None

        caller_hash = callgraph.frame_hash(caller)
        key = (caller_hash, backend, operation)

        try:
            exit_call = self._exit_calls[key]
            exit_call.timer.reset()  # ExitCall accounts for min, max, and sum (total)
        except KeyError:
            timer = self._timer_factory()
            self._exit_call_id += 1
            caller = callgraph.FrameInfo(caller)

            if self.incoming_correlation:
                sequence_info = self.incoming_correlation[correlation.EXIT_GUID_KEY] + '|' + str(self._exit_call_id)
            else:
                sequence_info = str(self._exit_call_id)

            exit_call = exitcalls.ExitCall(sequence_info, timer, backend, category, params, caller, operation=operation)
            self._exit_calls[key] = exit_call

        self._active_exit_call = exit_call
        exit_call.timer.start()
        return exit_call

    def end_exit_call(self, exc_info):
        """End the active exit call.

        Parameters
        ----------
        exc_info : (exc_type, exc_value, exc_tb) or None
            If an uncaught exception occurred during the exit call, then this
            contains the exception info (as returned by `sys.exc_info()`). If
            no exception occurred, then `None`.

        """
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

            self.add_exception(*exc_info)

        self._active_exit_call.add_call(exc_info)
        self._active_exit_call = None

    def add_error(self, error_info):
        """Add an error log to a BT.

        Parameters
        ----------
        error_info : errors.ErrorInfo
            An error info model to add to the BT's error list.

        See Also
        --------
        add_exception
            For reporting uncaught exceptions that occurred during the BT

        """
        self.errors.append(error_info)

    def is_exception_in_set(self, exc_value):
        if exc_value in self._exception_set:
            return True
        for arg in exc_value.args:
            if isinstance(arg, Exception):
                return self.is_exception_in_set(arg)
        return False

    def add_exception(self, exc_type, exc_value, exc_tb):
        """Add an exception to a BT.

        The arguments are those returned by sys.exc_info().

        Parameters
        ----------
        exc_type : type
            The type (class) of the raised exception
        exc_value
            The value of the raised exception
        exc_tb : traceback
            The traceback associated with the raised exception

        Returns
        -------
        errors.ExceptionInfo
            the exception info model added to the BT's exception list

        See Also
        --------
        add_error
            For reporting errors logged during the BT

        """
        # We may have added this exception already in an intercepted exit call.
        if self.is_exception_in_set(exc_value):
            return

        exc_info = errors.ExceptionInfo(exc_type, exc_value, exc_tb)

        if len(exc_info.stack_trace_frames):
            self.exceptions.append(exc_info)
            self._exception_set.add(exc_value)


def make_bt_info_request_dict(bt):
    if bt.incoming_correlation:
        correlation_header = bt.incoming_correlation.pb_dict
    else:
        correlation_header = None

    bt_info_request = {
        'requestID': bt.request_id,
        'messageID': 0,
        'btIdentifier': make_bt_identifier_dict(bt),
        'correlation': correlation_header,
    }

    if bt.cross_app_correlation:
        cross_app = make_cross_app_correlation_dict(bt.cross_app_correlation)
        bt_info_request.update(cross_app)

    return bt_info_request


def make_cross_app_correlation_dict(hdr):
    cross_app = {}

    backend_id = hdr.cross_app_correlation_backend

    if backend_id:
        cross_app['crossAppCorrelationBackendId'] = backend_id

    snap_enabled = bool(hdr[correlation.GUID_KEY] and hdr[correlation.SNAPSHOT_ENABLED_KEY])
    cross_app['incomingCrossAppSnapshotEnabled'] = snap_enabled

    return cross_app


def make_bt_identifier_dict(bt):
    if bt.registered_id:
        if bt.incoming_correlation:
            identifier_type = pb.BTIdentifier.REMOTE_REGISTERED
        else:
            identifier_type = pb.BTIdentifier.REGISTERED

        return {
            'type': identifier_type,
            'btID': bt.registered_id,
        }

    if bt.incoming_correlation:
        return make_remote_unregistered_bt_identifier_dict(bt)

    return {
        'type': pb.BTIdentifier.UNREGISTERED,
        'unregisteredBT': {
            'btInfo': {
                'entryPointType': bt.entry_type,
                'internalName': bt.name,
            },
            'customMatchPointDefinitionId': bt.custom_match_id,
        }
    }


def make_remote_unregistered_bt_identifier_dict(bt):
    if bt.naming_scheme_type:
        match_type = pb.UnRegisteredRemoteBT.DISCOVERED
        naming_scheme = bt.naming_scheme_type
    else:
        match_type = pb.UnRegisteredRemoteBT.CUSTOM
        naming_scheme = None

    return {
        'type': pb.BTIdentifier.REMOTE_UNREGISTERED,
        'unregisteredRemoteBT': {
            'entryPointType': bt.entry_type,
            'btName': u2b(bt.name),
            'matchCriteriaType': match_type,
            'namingSchemeType': naming_scheme,
        }
    }


def make_bt_details_dict(bt):
    if bt.bt_info_response:
        btInfoState = pb.BTDetails.RESPONSE_RECEIVED
    else:
        btInfoState = pb.BTDetails.MISSING_RESPONSE

    bt_details = {
        'btInfoRequest': bt.bt_info_request,
        'btMetrics': {
            'isError': bt.has_errors,
            'timeTaken': bt.timer.duration_ms,
            'timestamp': bt.timer.start_time_ms,
        },
        'btInfoState': btInfoState,
    }

    if bt._exit_calls:
        bt_details['btMetrics']['backendMetrics'] = exitcalls.make_backend_metrics_dicts(bt._exit_calls.values())

    if bt.snapshot_guid:
        bt_details['snapshotInfo'] = snapshot.make_snapshot_info_dict(bt)

    if bt.errors or bt.exceptions:
        bt_details['errors'] = errors.make_bt_errors_dict(bt.errors, bt.exceptions)

    return bt_details


def get_http_bt_name(naming, request, base_name):
    """Create a BT name based on naming properties and HTTP request data.

    Parameters
    ----------
    naming : mapping
        A naming scheme as specified as a set of key-value properties,
        retrieved from :py:class:`appdynamics.agent.core.registries.NamingSchemeRegistry`
    request : Request-like
        An object representing an incoming HTTP request, containing the
        attributes `method`, `headers`, `url` (the full URL with scheme),
        `cookies`, `path` (the path part of the URL), and `args` (query
        parameters). A Werkzeug `BaseRequest` is compatible, as are instances
        of :py:class:`appdynamics.lib.LazyWsgiRequest`
    base_name : str or None
        The base name for this BT, if any. If None or empty, then a base name
        will be generated from the request's `path` property according to the
        rules in the provided naming scheme

    Returns
    -------
    name : str
        The generated BT name

    """
    path = request.path

    if isinstance(path, unicode):
        path = path.encode('utf-8')

    path = [s for s in path.split('/') if s]

    strategy_to_input = {
        'header-value': 'headers',
        'cookie-value': 'cookies',
        'param-value': 'params',
    }

    def name(strategy, param, delim):
        if strategy == 'method':
            return request.method
        elif strategy == 'first-n-segments':
            return '/%s' % '/'.join(path[:int(param)])
        elif strategy == 'last-n-segments':
            return '/%s' % '/'.join(path[-int(param):])
        elif strategy == 'uri-segment-number':
            data_len = len(path)
            indices = sorted(int(i) - 1 for i in param.replace(' ', '').split(','))
            return delim.join(path[i] for i in indices if 0 <= i < data_len)
        elif strategy in strategy_to_input:
            data = getattr(request, strategy_to_input[strategy])
            keys = param.replace(' ', '').split(',')
            return '.'.join(data[k] for k in keys if data.get(k, None))

        return ''

    base_strategy = naming.get('uri-length') or 'first-n-segments'
    base_name = base_name or name(base_strategy, naming.get('segment-length') or 2, '')

    if 'uri-suffix-scheme' in naming:
        suffix = name(naming['uri-suffix-scheme'], naming.get('suffix-key', '0'), naming.get('delimiter', '.'))
    else:
        return base_name

    return '.'.join(p for p in (base_name, suffix) if p)
