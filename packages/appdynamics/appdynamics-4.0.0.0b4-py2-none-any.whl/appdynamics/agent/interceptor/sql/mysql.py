"""Intercept various MySQL database packages.

"""
import sys
from appdynamics.agent.interceptor import dbapi

VENDOR = 'MYSQL'


def get_mysql_backend_from_kwargs(*args, **kwargs):
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port', '3306')
    dbname = kwargs.get('database', kwargs.get('db', ''))
    backend = (VENDOR, host, str(port), dbname)
    return backend


def intercept_MySQLdb_connections(agent, mod):
    """Interceptor for MySQLdb.

    """
    mod.connect = mod.Connection = mod.Connect = dbapi.make_connect_interceptor(agent, get_mysql_backend_from_kwargs, mod.connect)


def intercept_mysql_connector_connection(agent, mod):
    """Interceptor for Oracle MySQL Connector/Python.

    This requires a different interception strategy than normal because
    Connector/Python allows users to establish a connection by directly
    creating instances of ``mysql.connector.MySQLConnection``. The ``connect``
    function just calls ``MySQLConnection`` with its arguments, so we have to
    patch the class instead of replacing ``connect``.

    """
    class MySQLConnection(mod.MySQLConnection):
        def _open_connection(self):
            self._appd_backend = (VENDOR, self._host, str(self._port), self._database)

            with agent.db_exit_call(sys._getframe(2), self._appd_backend, 'connect'):
                super(MySQLConnection, self)._open_connection()

        def cursor(self, *args, **kwargs):
            real_cursor = super(MySQLConnection, self).cursor(*args, **kwargs)
            instrumented_cursor = dbapi.InstrumentedCursor(agent, self._appd_backend, real_cursor)
            return instrumented_cursor

    MySQLConnection.appd_orig_class = mod.MySQLConnection
    mod.MySQLConnection = MySQLConnection
