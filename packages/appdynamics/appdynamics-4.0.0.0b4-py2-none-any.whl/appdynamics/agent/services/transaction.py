import logging
from Queue import Queue, Empty
import threading

from appdynamics.agent.core import snapshot
from appdynamics.agent.core.transport import InfoTransport, ReportingTransport

from appdynamics.agent.models import transactions, exitcalls


class TransactionService(object):
    """Retrieves and reports information about transactions via the proxy.

    """

    RECV_TIMEOUT_MS = 100

    def __init__(self, info_socket_name, reporting_socket_name, snapshot_svc):
        super(TransactionService, self).__init__()

        self.enabled = False

        self.logger = logging.getLogger('appdynamics.agent')
        self.info_socket_name = info_socket_name
        self.reporting_transport_name = reporting_socket_name
        self.need_to_reconnect = False

        self.snapshot_svc = snapshot_svc
        self.work_q = Queue()

        self.connect_event = threading.Event()
        self.base_addr = None

        self.thread = None
        self.started_event = threading.Event()
        self.work_completed_event = threading.Event()

    def is_running(self):
        return self.thread is not None

    def start(self):
        assert self.thread is None
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def connect(self, base_addr):
        self.need_to_reconnect = True
        self.base_addr = base_addr
        self.connect_event.set()

    def disconnect(self):
        self.enabled = False
        self.started_event.clear()
        self.connect_event.clear()

    def wait_for_start(self, timeout_ms=None):
        if timeout_ms is not None:
            self.started_event.wait(timeout_ms / 1000.)
        else:
            self.started_event.wait()

    def wait_for_end(self, timeout_ms):
        if timeout_ms is not None:
            self.work_completed_event.wait(timeout_ms / 1000.)
        else:
            self.work_completed_event.wait()

    def _add_work(self, operation, payload):
        self.work_completed_event.clear()
        self.work_q.put((operation, payload), block=False)

    def _get_work(self):
        return self.work_q.get()

    def start_transaction(self, bt):
        if not self.enabled:
            self.logger.warning('BT:%s (name=%r) skipped because TxService is disabled')
            return

        self.logger.debug('BT:%s (name=%r) start transaction', bt.request_id, bt.name)

        with bt.lock:
            bt.timer.start()
            self._start_or_schedule_snapshot(bt)

        self._add_work(self._do_start_transaction, bt)

    def end_transaction(self, bt):
        self.logger.debug('BT:%s (name=%r) end transaction', bt.request_id, bt.name)

        with bt.lock:
            bt.timer.stop()

            if bt.bt_info_response:
                if bt.has_errors and bt.snapshot_guid is None:
                    # If we ended without a snapshot but had errors, add the snapshot now.
                    self._start_or_schedule_snapshot(bt)

            if bt.snapshotting:
                self.snapshot_svc.end_snapshot(bt)

        if self.enabled:
            self._add_work(self._do_report_transaction, bt)

    def reresolve(self, backend_id):
        self._add_work(self._do_reresolve, backend_id)

    def discard_work(self):
        try:
            self.logger.debug('TxService discarding all work')
            while True:  # Eat the queue items until get() raises Empty
                self.work_q.get(block=False)
        except Empty:
            self.work_completed_event.set()

    def _do_start_transaction(self, info_transport, reporting_transport, bt):
        bt.bt_info_request = transactions.make_bt_info_request_dict(bt)
        info_transport.send(bt.bt_info_request)
        self.logger.debug('BT:%s (name=%r) send BTInfoRequest:\n%s', bt.request_id, bt.name, bt.bt_info_request)

        response = info_transport.recv(timeout_ms=self.RECV_TIMEOUT_MS)

        if response is None:
            self.logger.warning(
                'BT:%s (name=%r) timeout waiting for BTInfoResponse (timeout=%dms)',
                bt.request_id, bt.name, self.RECV_TIMEOUT_MS)
            self.logger.critical('Proxy does not seem to be responding; discarding all pending BTs and disabling TxService')
            self.disconnect()
            self.discard_work()
            return

        self.logger.debug('BT:%s (name=%r) recv BTInfoResponse:\n%s', bt.request_id, bt.name, response)

        if response.requestID != bt.request_id:
            self.logger.warning(
                'BT:%s (name=%r) got unexpected response (BTInfoResponse.requestID=%s)',
                bt.request_id, bt.name, response.requestID)

            skipped = 0

            # Skip responses until there are no more, or we find the pair to the request we sent.
            while response and response.requestID != bt.request_id:
                response = info_transport.recv()
                skipped += 1

            if skipped:
                self.logger.warning(
                    'BT:%s (name=%r) skipped %d responses %s',
                    bt.request_id, bt.name, skipped, 'and found match' if response else 'without matching')

        with bt.lock:
            bt.bt_info_response = response
            self._start_or_schedule_snapshot(bt)

    def _do_report_transaction(self, info_transport, reporting_transport, bt):
        self.logger.debug('BT:%s (name=%r) sending BT details bt_info_request=%s', bt.request_id, bt.name, bt.bt_info_request)
        if not bt.bt_info_request:
            raise Exception('Cannot send details for BT:%s (name=%r) because it has no BTInfoRequest' % (bt.request_id, bt.name))
        reporting_transport.send_bt_details(transactions.make_bt_details_dict(bt))

    def _do_reresolve(self, info_transport, reporting_transport, backend_id):
        reporting_transport.send_reresolution(exitcalls.make_backend_reresolve_dict(backend_id))

    def _run(self):
        info_transport = InfoTransport(self.info_socket_name)
        reporting_transport = ReportingTransport(self.reporting_transport_name)
        first_connect = True

        while self.is_running():
            self.connect_event.wait()

            if self.need_to_reconnect:
                if first_connect:
                    first_connect = False
                    self.logger.info('TxService connecting to proxy')
                else:
                    self.logger.info('TxService attempting to reconnect to proxy')
                    info_transport.disconnect()
                    reporting_transport.disconnect()

                self.need_to_reconnect = False

                info_transport.connect(self.base_addr)
                reporting_transport.connect(self.base_addr)

                self.enabled = True
                self.started_event.set()

            operation, payload = self._get_work()
            operation(info_transport, reporting_transport, payload)

            if self.work_q.empty():
                self.work_completed_event.set()

    def _start_or_schedule_snapshot(self, bt):
        """Helper for determining whether and how to start a snapshot.

        This method does nothing if the BT is currently snapshotting or if the
        BT has already taken a snapshot. This method may be safely called with
        a BT that has already ended.

        """

        if bt.snapshot_guid is not None:  # Snapshot already taken
            return

        response = bt.bt_info_response

        if bt.continuing_snapshot_enabled:
            # If we are continuing from a BT that is snapshotting, we add a
            # snapshot. (We do this even if our BT has already ended, adding
            # an empty snapshot because the controller expects snapshots for
            # this BT.)
            self.snapshot_svc.start_snapshot(bt, snapshot.CONTINUING)
        elif bt.has_errors:
            # If the BT has errors, we need to attach an ERROR snapshot. The
            # ERROR snapshot is what populates the "occurences of this error"
            # UI in the controller.
            self.snapshot_svc.start_snapshot(bt, snapshot.ERROR)
        elif response:
            if response.isSnapshotRequired:
                # A snapshot is required by the controller for diagnostic
                # sessions, periodic collection, and where the controller
                # detects a BT has violated expectations (e.g., sustained
                # high response times or error rates).
                self.snapshot_svc.start_snapshot(bt, snapshot.REQUIRED)
            elif response.currentSlowThreshold:
                # If we have a slow threshold that has already expired, immediately
                # start a snapshot (even if the BT has completed). Otherwise, if the
                # BT hasn't ended, yet, schedule the BT.
                if bt.timer.duration_ms >= response.currentSlowThreshold:
                    self.snapshot_svc.start_snapshot(bt, snapshot.SLOW)
                elif not bt.completed:
                    self.snapshot_svc.schedule_snapshot(bt, response.currentSlowThreshold)
