from contextlib import contextmanager
import logging
import sys
import time

from appdynamics import config, get_version
from appdynamics.lib import get_ident, values

from appdynamics.agent import pb
from appdynamics.agent.core import correlation, timer, registries

from appdynamics.agent.models.transactions import make_transaction_factory

from appdynamics.agent.services.config import ConfigService
from appdynamics.agent.services.proxycontrol import ProxyControlService
from appdynamics.agent.services.snapshot import SnapshotService
from appdynamics.agent.services.transaction import TransactionService


class Agent(object):
    """The entry point for the Python agent.

    """

    def __init__(self):
        super(Agent, self).__init__()

        self.logger = logging.getLogger('appdynamics.agent')

        self.app_id = None
        self.tier_id = None
        self.node_id = None
        self.account_guid = None
        self.controller_guid = None

        self._tx_factory = make_transaction_factory(self.timer)

        # Services
        self.proxy_control_svc = None
        self.config_svc = None
        self.tx_svc = None
        self.snapshot_svc = None

        # Registries
        self.naming_registry = None
        self.bt_registry = None
        self.backend_registry = None
        self.error_config_registry = None

        self.active_bts = {}

    def start(self):
        if self.proxy_control_svc is None:
            self.logger.info('Starting AppDynamics Python agent (build %s) ...' % get_version())
            self.proxy_control_svc = ProxyControlService(self.on_start_node_response)
            self.proxy_control_svc.start()

    def wait_for_start(self, timeout_ms=None):
        """Wait for the agent to start and get configured.

        Other Parameters
        ----------------
        timeout_ms : int, optional
            The maximum time to wait for the agent to start and be configured
            before returning.

        Returns
        -------
        bool
            Returns ``True`` if the agent is enabled after waiting, else
            ``False``.

        """
        if timeout_ms is not None:
            with self.timer() as timer:
                self.proxy_control_svc.wait_for_start(timeout_ms=timeout_ms)

                if self.config_svc is not None:
                    timeout_ms = max(0, timeout_ms - timer.duration_ms)
                    self.config_svc.wait_for_config(timeout_ms=timeout_ms)

                if self.tx_svc is not None:
                    timeout_ms = max(0, timeout_ms - timer.duration_ms)
                    self.tx_svc.wait_for_start(timeout_ms=timeout_ms)
        else:
            self.proxy_control_svc.wait_for_start()
            self.config_svc.wait_for_config()
            self.tx_svc.wait_for_start()

        return self.enabled

    def wait_for_end(self, timeout_ms=None):
        """Wait for the agent to finish reporting any pending BTs.

        """
        self.tx_svc.wait_for_end(timeout_ms=timeout_ms)

    @property
    def started(self):
        """Return true if the agent has been started.

        Even if this property returns true, it's possible the agent has
        started but is in a disabled state.

        """
        return bool(self.proxy_control_svc)

    @property
    def enabled(self):
        """Return true if the agent has started and is enabled.

        """
        return (
            self.started and
            self.config_svc and self.config_svc.enabled and
            self.tx_svc and self.tx_svc.enabled)

    def timer(self, *args, **kwargs):
        """Create a timer.

        Returns
        -------
        timer : appdynamics.agent.core.timer.Timer
            The newly created timer. Note the returned timer has not been
            started; you must start it with its
            :py:meth:`appdynamics.agent.core.timer.Timer.start()` method.

        """
        t = timer.Timer(self.time, *args, **kwargs)
        return t

    def time(self):
        """Get the current time in ms from the agent's timer.

        Returns
        -------
        int
            The current time in milliseconds.

        """
        return int(1000 * time.time())

    def on_start_node_response(self, response):
        if self.config_svc is None:
            self.logger.info('Starting AppDynamics agent services...')

            initial_config = response.configResponse if response.HasField('configResponse') else None

            self.bt_registry = registries.TransactionRegistry()
            self.backend_registry = registries.BackendRegistry()
            self.naming_registry = registries.NamingSchemeRegistry()
            self.error_config_registry = registries.ErrorConfigRegistry()

            self.config_svc = ConfigService(config.PROXY_CONFIG_SOCKET_NAME,
                                            self.update_config,
                                            self.proxy_control_svc.reconnect,
                                            initial_config)

            self.snapshot_svc = SnapshotService(self)

            self.tx_svc = TransactionService(
                config.PROXY_INFO_SOCKET_NAME, config.PROXY_REPORTING_SOCKET_NAME,
                self.snapshot_svc)

            self.logger.info('Starting AppDynamics BT, config and snapshot threads...')
            self.tx_svc.start()
            self.config_svc.start()
            self.snapshot_svc.start()

        data_dir = response.dataSocketDirPath
        self.logger.info('Connecting AppDynamics services to %s...', data_dir)
        self.config_svc.connect(data_dir)
        self.tx_svc.connect(data_dir)

    def update_config(self, config):
        if self.app_id is None and config.HasField('agentIdentity'):
            identity = config.agentIdentity
            self.app_id = identity.appID
            self.tier_id = identity.tierID
            self.node_id = identity.nodeID
            self.account_guid = identity.accountGUID
            self.controller_guid = identity.controllerGUID

        self.bt_registry.update_config(config.txInfo)
        self.backend_registry.update_config(config.bckInfo)
        self.naming_registry.update_config(config.txConfig)
        self.error_config_registry.update_config(config.errorConfig)

    def start_transaction(self, entry_type, base_name=None, request=None, correlation_header=None):
        """Start a new business transaction.

        Parameters
        ----------
        entry_type : int
            An ENTRY_xxx from :py:mod:`appdynamics.agent.models.transactions`.
        base_name : str, optional
            The base name to give the transaction. If `None`, then the name is
            computed from `request`.
        request : object, optional
            The active, incoming HTTP request that caused this BT, if any.
            This must have fields `method`, `url`, `path`, `args` (the query
            parameters), `cookies`, and `headers`.
        correlation_header : str, optional
            The incoming correlation header as a string, if any. If this is
            `None` or not passed, and `request` is passed, then the header
            is extracted from the `request` object. (You can pass in an empty
            string if you want to explicitly disable correlation regardless
            of what is in the `request` header.)

        Returns
        -------
        bt : Transaction or None
            If a transaction was started, it is returned. A transaction will
            not be started and `None` will be returned if (1) the agent is
            disabled; (2) if the transaction that would've been started is
            excluded from reporting by the agent's configuration; (3) if
            there is an incoming correlation header that disables transaction
            detection.

        """
        bt = self.active_bts.get(get_ident())
        if bt:
            return bt

        if not self.started:
            self.start()
            return None

        if not self.enabled:
            return None

        entry_type_name = pb.EntryPointType.Name(entry_type)

        if request and correlation_header is None:
            correlation_header = request.headers.get(correlation.HEADER_NAME)

        bt_name = None

        try:
            bt_name, match = self._name_bt(base_name, entry_type, request)
            correlation_header = self.parse_correlation_header(correlation_header)

            if correlation_header is None or correlation_header.is_cross_app:
                bt = self._start_bt(bt_name, entry_type, match)
                bt.cross_app_correlation = correlation_header

                self.logger.debug(
                    "BT:%s (name=%r) entry=%s start=new registered_id=%r %s",
                    bt.request_id, bt.name, entry_type_name, bt.registered_id,
                    '[x-app]' if correlation_header else '')
            else:  # In app correlation
                assert not correlation_header.is_cross_app
                bt = self._continue_bt(correlation_header)
                self.logger.debug(
                    'BT:%s (name=%r) entry=%s/%s start=continuing header: %s',
                    bt.request_id, bt.name, entry_type_name, bt.entry_type, bt.incoming_correlation)
        except IgnoreTransaction as exc:
            self.logger.debug('BT:IGNORED (name=%r) entry=%s reason=%s', bt_name, entry_type_name, exc.message)
            return None

        bt.request = request
        self.active_bts[get_ident()] = bt
        self.tx_svc.start_transaction(bt)
        return bt

    def _name_bt(self, base_name, entry_type, request):
        if request:
            match = self.naming_registry.match(entry_type, request, base_name)

            if match is None:
                raise IgnoreTransaction('no name for BT -- discovery disabled or BT matched exclude rule')

            bt_name = match.name
        else:
            bt_name = base_name
            match = None

        if self.bt_registry.is_excluded(entry_type, bt_name):
            raise IgnoreTransaction('excluded by rule')

        return bt_name, match

    def _continue_bt(self, correlation_header):
        if self.check_for_reresolution(correlation_header):
            raise IgnoreTransaction('reresolution, tier: %d, header: %s' % (self.tier_id, correlation_header))

        return self._tx_factory(incoming_correlation=correlation_header)

    def _start_bt(self, bt_name, entry_type, match):
        registered_id = self.bt_registry.get_registered_id(entry_type, bt_name)
        bt = self._tx_factory(entry_type=entry_type, name=bt_name, registered_id=registered_id)

        if match:
            bt.custom_match_id = match.custom_match_id
            bt.naming_scheme_type = match.naming_scheme

        return bt

    @property
    def can_cross_app_correlate(self):
        return self.controller_guid and self.account_guid

    def parse_correlation_header(self, correlation_header):
        if not correlation_header:
            return None

        hdr = correlation.parse_header(correlation_header, self.app_id)

        if hdr[correlation.DISABLE_TX_DETECTION_KEY]:
            raise IgnoreTransaction('notxdetect, header: %s' % correlation_header)

        incoming_controller_guid = hdr[correlation.CONTROLLER_GUID_KEY]
        incoming_account_guid = hdr[correlation.ACCOUNT_GUID_KEY]
        incoming_app_id = hdr[correlation.APP_ID_KEY]

        if incoming_controller_guid != self.controller_guid:
            self.logger.debug(
                'Do not correlate: controller GUID in header is %r but ours is %r',
                incoming_controller_guid, self.controller_guid)
            return None

        if incoming_account_guid != self.account_guid:
            self.logger.debug(
                'Do not correlate: account GUID in header is %r but ours is %r',
                incoming_account_guid, self.account_guid)
            return None

        if hdr.is_cross_app and not self.can_cross_app_correlate:
            self.logger.debug(
                'Do not correlate: cross-app is disabled; app ID in header is %r but ours is %r',
                incoming_app_id, self.app_id)
            return None

        return hdr

    def check_for_reresolution(self, correlation_header):
        """Check if re-resolution is required.

        Parameters
        ----------
        correlation_header : correlation.CorrelationHeader

        Returns
        -------
        bool
            ``True`` if we re-resolved the backend, else ``False``.

        """
        try:
            backend_id = int(correlation_header[correlation.UNRESOLVED_EXIT_ID_KEY])

            if backend_id > 0:
                last_tier_id = self.backend_registry.get_component_for_registered_backend(backend_id)

                if last_tier_id is not None and last_tier_id != self.tier_id:
                    self.tx_svc.reresolve(backend_id)
                    return True

                to_app_id = correlation_header.cross_app_to_component

                if to_app_id and to_app_id != self.app_id:
                    self.tx_svc.reresolve(backend_id)
                    return True
        except:
            pass

        return False

    def get_active_bt(self):
        """Get the active business transaction for the calling context.

        The calling context is the active greenlet or thread, depending on
        whether greenlets are in use or not. If the agent is disabled, or if
        there is no active transaction for the calling context, None is
        returned.

        Returns
        -------
        bt : appdynamics.agent.core.bt.Transaction or None
            the active business transaction (if any)

        """
        return self.enabled and self.active_bts.get(get_ident(), None)

    @contextmanager
    def db_exit_call(self, caller, backend_id, operation, params=None):
        """Context manager for instrumenting DB exit calls.

        Parameters
        ----------
        caller : frame
        backend_id : tuple
            A tuple of the database backend's identifying properties.
        operation : str
            The operation being performed, such as a SQL query.
        params : iterable, optional
            The parameters passed to the operation (i.e., the query parameters
            passed to the SQL query), if any. The default is `None`, which
            corresponds to no parameters.

        """
        bt = self.get_active_bt()
        backend = bt and self.backend_registry.get_db_backend(*backend_id)

        if backend:
            exc_info = None

            try:
                bt.start_exit_call(caller, backend, operation=operation, params=params)
                yield
            except:
                exc_info = sys.exc_info()
                self.logger.exception("exception in start_exit_call")
                raise
            finally:
                bt.end_exit_call(exc_info)
        else:
            yield

    def end_transaction(self, exc, bt=None):
        """End the active transaction on this thread.

        Parameters
        ----------
        exc : BaseException or None
            If an uncaught exception caused the transaction to end, it is
            passed here. Otherwise, `None` is passed.

        bt : appdynamics.agent.models.transactions.Transaction, optional
            A specific BT to end.  Note: if this parameter is used, exc, must
            be a tuple as returned from sys.exc_info().

        """
        bt = bt or self.active_bts.pop(get_ident(), None)
        if self.enabled and bt:
            error_config = self.error_config_registry
            if error_config.should_detect_errors and error_config.mark_transaction_as_error:
                if exc:
                    if isinstance(exc, tuple):
                        exc_info = exc
                    else:
                        exc_info = sys.exc_info()
                    bt.add_exception(*exc_info)

                bt.has_errors = bool(bt.errors or not all(error_config.is_exception_ignored(e) for e in bt.exceptions))

            self.tx_svc.end_transaction(bt)

    def end_active_bts(self):
        """End all the active BTs.

        """
        for bt in values(self.active_bts):
            self.end_transaction(None, bt=bt)


class IgnoreTransaction(Exception):
    def __init__(self, message):
        super(IgnoreTransaction, self).__init__()
        self.message = message
