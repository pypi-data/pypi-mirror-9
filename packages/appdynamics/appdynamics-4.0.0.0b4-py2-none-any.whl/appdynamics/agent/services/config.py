import logging
import time
import threading

from appdynamics.agent.core.transport import ConfigTransport
from appdynamics.agent.pb import ConfigResponse
from appdynamics.lib import merge_protobuf


class ConfigService(threading.Thread):
    """A service that fetches and updates configuration.

    """

    UNREGISTERED = ConfigResponse.UNREGISTERED
    REGISTERED = ConfigResponse.REGISTERED
    INITIALIZED = ConfigResponse.INITIALIZED
    DISABLED = ConfigResponse.DISABLED

    RECONFIGURATION_INTERVAL_MS = 10000
    RECEIVE_TIMEOUT_MS = 1000

    def __init__(self, socket_name, update_agent_config, reconnect_proxy, initial_config):
        super(ConfigService, self).__init__()

        self.socket_name = socket_name
        self.update_agent_config = update_agent_config
        self.reconnect_proxy = reconnect_proxy
        self.connect_event = threading.Event()
        self.base_addr = None
        self.running = False
        self.lock = threading.Lock()
        self.logger = logging.getLogger('appdynamics.agent')
        self.last_version = -1
        self.config = ConfigResponse()
        self.connected = False
        self._state = self.UNREGISTERED
        self.daemon = True

        self.config_ready_event = threading.Event()

        if initial_config is not None:
            self._update_config(initial_config)

    def connect(self, base_addr):
        if not self.connected:
            self.base_addr = base_addr
            self.connect_event.set()

    def _update_config(self, new_config):
        self.config_ready_event.set()
        self.last_version = new_config.currentVersion
        self.state = new_config.agentState

        merge_protobuf(self.config, new_config)
        self.logger.debug('Merged incoming config:\n%s' % self.config)

        self.update_agent_config(self.config)

    @property
    def enabled(self):
        return self.state not in (self.UNREGISTERED, self.DISABLED)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        with self.lock:
            was_enabled = self.enabled
            self._state = new_state

        if not was_enabled and self.enabled:
            self.logger.info('Initializing disabled/unregistered Python agent.')
        elif was_enabled and not self.enabled:
            self.logger.info('Disabling Python agent.')

    def wait_for_config(self, timeout_ms=None):
        """Wait for configuration.

        """
        if timeout_ms is not None:
            self.config_ready_event.wait(timeout_ms / 1000.)
        else:
            self.config_ready_event.wait()

    def run(self):
        self.running = True
        transport = ConfigTransport(self.socket_name)

        while self._is_running():
            # Don't do anything if we haven't connected yet or we are waiting to reconnect.
            self.connect_event.wait()

            if not self.connected:
                self._connect(transport)
            else:
                # We check for new config periodically; if we haven't just connected, go to sleep for a while.
                time.sleep(self.RECONFIGURATION_INTERVAL_MS/1000.)

            self._send_config_request(transport)
            self._fetch_and_update_config(transport)

    def _connect(self, transport):
        self.connected = True
        transport.disconnect()
        transport.connect(self.base_addr)

    def _send_config_request(self, transport):
        transport.send({'lastVersion': self.last_version})

    def _fetch_and_update_config(self, transport):
        response = transport.recv(timeout_ms=self.RECEIVE_TIMEOUT_MS)

        if response:
            self.logger.debug('Got config response = \n%s', response)

            if not response.HasField('currentVersion') or not response.HasField('agentState'):
                self.logger.error('Config response missing currentVersion or agentState.')
                return

            current_version = response.currentVersion

            if current_version > self.last_version:
                self._update_config(response)
            elif current_version < self.last_version:
                self.logger.warning('Got older config (%d) when last_verison = %d', current_version,
                                    self.last_version)
            else:
                self.logger.debug('Config unchanged on response (version = %d)', current_version)
        else:
            # Timed out waiting for a config response.  Set state to disabled, trigger a reconnection and unset the
            # connect event in order to stop trying to get new config.
            self.logger.warning('Did not get config response after %dms --  triggering reconnection.',
                                self.RECEIVE_TIMEOUT_MS)

            self._reconnect()

    def _reconnect(self):
        self.state = self.DISABLED
        self.connected = False
        self.config_ready_event.clear()
        self.connect_event.clear()
        self.reconnect_proxy()

    def _is_running(self):
        return self.running
