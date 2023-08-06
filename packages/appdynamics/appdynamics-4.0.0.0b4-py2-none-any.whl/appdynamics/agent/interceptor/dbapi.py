from functools import wraps
import sys


def make_connect_interceptor(agent, backend_naming_fn, connect_fn):
    @wraps(connect_fn)
    def connect(*args, **kwargs):
        try:
            backend = backend_naming_fn(*args, **kwargs)
        except:
            agent.logger.warning('could not name backend: %s', backend_naming_fn.__name__)
            return connect_fn(*args, **kwargs)

        with agent.db_exit_call(sys._getframe(1), backend, 'connect'):
            real_conn = connect_fn(*args, **kwargs)
            instrumented_conn = InstrumentedConnection(agent, backend, real_conn)
        return instrumented_conn

    connect.appd_orig_connect = connect_fn
    return connect


class InstrumentedConnection(object):
    def __init__(self, agent, backend, conn):
        super(InstrumentedConnection, self).__init__()
        self._appd_agent = agent
        self._appd_backend = backend
        self._appd_conn = conn

    def __getattribute__(self, name):
        if name in ('_appd_agent', '_appd_backend', '_appd_conn', 'cursor'):
            return object.__getattribute__(self, name)
        conn = object.__getattribute__(self, '_appd_conn')
        return getattr(conn, name)

    def cursor(self, *args, **kwargs):
        agent = object.__getattribute__(self, '_appd_agent')
        backend = object.__getattribute__(self, '_appd_backend')
        conn = object.__getattribute__(self, '_appd_conn')

        real_cursor = conn.cursor(*args, **kwargs)
        instrumented_cursor = InstrumentedCursor(agent, backend, real_cursor)
        return instrumented_cursor


class InstrumentedCursor(object):
    def __init__(self, agent, backend, cursor):
        super(InstrumentedCursor, self).__init__()
        self._appd_agent = agent
        self._appd_backend = backend
        self._appd_cursor = cursor

    def __getattribute__(self, name):
        if name in ('_appd_agent', '_appd_backend', '_appd_cursor', 'execute', '__iter__'):
            return object.__getattribute__(self, name)
        cursor = object.__getattribute__(self, '_appd_cursor')
        return getattr(cursor, name)

    def __iter__(self):
        cursor = object.__getattribute__(self, '_appd_cursor')
        return iter(cursor)

    def execute(self, operation, parameters=None):
        agent = object.__getattribute__(self, '_appd_agent')
        backend = object.__getattribute__(self, '_appd_backend')
        cursor = object.__getattribute__(self, '_appd_cursor')

        with agent.db_exit_call(sys._getframe(1), backend, operation, parameters):
            return cursor.execute(operation, parameters)
