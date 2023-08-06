import imp
import sys
import logging
import logging.handlers
import os
import re
from appdynamics.lib import default_log_formatter, running_tests


def get_ucs():
    ucs = 'ucs4' if sys.maxunicode > 65535 else 'ucs2'
    return ucs


# Les fossoyeurs de l'esperance affutent leurs longs couteaux.
def make_virtual_bindeps_package():
    """Workaround for lack of Python 2.x ABI.

    The embedded zmq libraries are specific to cp27m, cp27mu, etc. builds
    because they look for the UTF8/UTF16 string versions. Unfortunately, we
    have no way of specifying the Python ABI as part of the dependencies, so
    we can't take the correct precompiled version.

    Instead, we have bindeps ship the wide and narrow Unicode versions, and
    then construct a "virtual" bindeps package by symlinking the right
    version. We have to do this instead of just aliasing the import because
    there's otherwise no way to deal with the "appdynamics_bindes.zmq"
    imports inside the zmq code.

    """
    import appdynamics_bindeps
    import platform
    import tempfile

    pyver = ''.join(platform.python_version_tuple()[:2])
    ucs = get_ucs()
    prefix = "%s-%s" % (pyver, ucs)

    tmp_root = tempfile.mkdtemp(prefix=prefix)
    src_root = os.path.dirname(appdynamics_bindeps.__file__)
    dest = os.path.join(tmp_root, os.path.basename(src_root))

    del sys.modules['appdynamics_bindeps']

    os.makedirs(dest)
    zmq_target = 'zmq_' + ucs

    for fn in os.listdir(src_root):
        src = os.path.join(src_root, fn)

        if fn == zmq_target:
            os.symlink(src, os.path.join(dest, 'zmq'))
        elif not fn.startswith('zmq'):
            os.symlink(src, os.path.join(dest, fn))

    sys.path.insert(0, tmp_root)


def import_zmq():
    try:
        __import__('appdynamics_bindeps.zmq')
    except ImportError:
        make_virtual_bindeps_package()


import_zmq()


from appdynamics.agent.core.agent import Agent
from appdynamics.agent.interceptor import add_hook, http, sql, frameworks, cache, logging as appd_logging
from appdynamics import config


_agent = None


BT_INTERCEPTORS = (
    # Entry points
    ('flask', frameworks.intercept_flask),
    ('django.core.handlers.wsgi', frameworks.intercept_django_wsgi_handler),
    ('django.core.handlers.base', frameworks.intercept_django_base_handler),
    ('cherrypy', frameworks.intercept_cherrypy),

    # HTTP exit calls
    ('httplib', http.intercept_httplib),
    ('urllib3', http.intercept_urllib3),
    ('requests', http.intercept_requests),
    ('boto.https_connection', http.intercept_boto),

    # Database exit calls
    ('psycopg2', sql.psycopg2.intercept_psycopg2),
    ('MySQLdb', sql.mysql.intercept_MySQLdb_connections),
    ('mysql.connector.connection', sql.mysql.intercept_mysql_connector_connection),

    # Caches
    ('redis.connection', cache.intercept_redis),
    ('memcache', cache.intercept_memcache),

    # Logging
    ('logging', appd_logging.intercept_logging),
)


def configure(environ=None):
    agent_config = config.parse_environ()
    if environ:
        agent_config.update(config.parse_environ(environ))

    config.merge(agent_config)

    if not running_tests():
        configure_logging()

    return config.validate_config(agent_config)


def get_log_level():
    default_logging_level = logging.WARNING
    allowed_logging_levels = {'WARNING': logging.WARNING, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG}

    level = config.LOGGING_LEVEL.upper()
    return allowed_logging_levels.get(level, default_logging_level)


def get_log_filename():
    non_alphanumeric = re.compile(r'\W+')
    sanitize = lambda x: non_alphanumeric.sub('_', x)
    filename = '-'.join(map(sanitize, [config.APP_NAME, config.NODE_NAME])) + '.log'
    return os.path.join(config.LOGS_DIR, filename)


def is_debugging():
    return config.DEBUG_LOG


def configure_logging():
    """Configure the appdynamics agent logger.

    By default, we configure a log file which rolls over at midnight and keeps a week's worth of logs.  If the logging
    debug flag is set, we set the logging level to DEBUG and enable a handler to stderr.

    """
    try:
        debug = is_debugging()

        if debug:
            level = logging.DEBUG
        else:
            level = get_log_level()

        logger = logging.getLogger('appdynamics.agent')
        logger.setLevel(level)

        timed_file_handler = logging.handlers.TimedRotatingFileHandler(get_log_filename(), when='midnight',
                                                                       backupCount=7)
        timed_file_handler.setLevel(level)
        timed_file_handler.setFormatter(default_log_formatter)
        logger.addHandler(timed_file_handler)

        if debug:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(level)
            stream_handler.setFormatter(default_log_formatter)
            logger.addHandler(stream_handler)

        logger.propagate = False
    except:
        logging.getLogger('appdynamics.agent').exception('Logging configuration failed.')


def bootstrap(agent=None):
    try:
        global _agent

        _agent = agent or Agent()
        hook = add_hook(_agent)

        for mod, patch in BT_INTERCEPTORS:
            hook.call_on_import(mod, patch)

        _agent.module_interceptor = hook
        return _agent
    except:
        logging.getLogger('appdynamics.agent').exception('Error bootstrapping AppDynamics agent; disabling.')
        return None


def bootstrap_tear_down():
    global _agent

    # Remove the hook and discard the agent.
    try:
        sys.meta_path.remove(_agent.module_interceptor)
    except:
        pass
    _agent = None


def get_agent_instance():
    if _agent is None:
        return bootstrap()
    else:
        return _agent


def remove_autoinject():
    # Remove our injected sitecustomize and load the real one (if any).
    # We let this throw an ImportError because `site` already silences it.
    sys.modules.pop('sitecustomize', None)
    mod_data = imp.find_module('sitecustomize')
    mod = imp.load_module('sitecustomize', *mod_data)
    sys.modules.update(sitecustomize=mod)
