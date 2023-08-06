import imp
import sys
from functools import wraps

import appdynamics.agent
from appdynamics import config
from appdynamics.lib import LazyWsgiRequest
from appdynamics.agent.models.transactions import ENTRY_WSGI
from appdynamics.agent.interceptor.base import EntryPointInterceptor


class WSGIInterceptor(EntryPointInterceptor):
    def __init__(self, agent, cls, entry_type=ENTRY_WSGI):
        self.entry_type = entry_type
        super(WSGIInterceptor, self).__init__(agent, cls)

    def application_callable(self, application, instance, environ, start_response):
        self.start_transaction(self.entry_type, request=LazyWsgiRequest(environ))
        result = application(instance, environ, self._make_start_response_wrapper(start_response))
        self.end_transaction()
        return result

    def _make_start_response_wrapper(self, start_response):
        @wraps(start_response)
        def start_response_wrapper(status, headers, exc_info=None):
            """Extract the HTTP status code and add an error to the BT if required.

            See https://www.python.org/dev/peps/pep-0333/#the-start-response-callable for more information.

            """
            with self.log_exceptions():
                bt = self.bt
                if bt:
                    status_code, msg = status.split(' ', 1)
                    bt.status_code = status_code
                    http_error = self.agent.error_config_registry.get_http_error(int(status_code), msg)
                    if http_error:
                        self.bt.add_error(http_error)
            return start_response(status, headers, exc_info)
        return start_response_wrapper


class WSGIApplication(object):
    def __init__(self):
        self._application = None
        self._configured = False

    def load_application(self):
        wsgi_callable = config.WSGI_CALLABLE_OBJECT or 'application'

        if not config.WSGI_SCRIPT_ALIAS and not config.WSGI_MODULE:
            raise AttributeError(
                'Cannot get WSGI application: the AppDynamics agent cannot load your '
                'application. You must set either APPD_WSGI_SCRIPT_ALIAS or APPD_WSGI_MODULE '
                'in order to load your application.')

        if config.WSGI_MODULE:
            module_name = config.WSGI_MODULE

            if ':' in module_name:
                module_name, wsgi_callable = module_name.split(':', 1)

            __import__(module_name)
            wsgi_module = sys.modules[module_name]
        else:
            wsgi_module = imp.load_source('wsgi_module', config.WSGI_SCRIPT_ALIAS)

        if wsgi_callable.endswith('()'):  # "Quick" callback
            app = getattr(wsgi_module, wsgi_callable[:-2])
            app = app()
        else:
            app = getattr(wsgi_module, wsgi_callable)

        self._application = app

    def wsgi_application(self, environ, start_response):
        return self._application(environ, start_response)

    def __call__(self, environ, start_response):
        if not self._configured:
            appdynamics.agent.configure(environ)
            self._configured = True

        if not self._application:
            self.load_application()

        return self.wsgi_application(environ, start_response)


def get_wsgi_application():
    from appdynamics.agent import get_agent_instance
    WSGIInterceptor(get_agent_instance(), WSGIApplication).attach('wsgi_application',
                                                                  patched_method_name='application_callable')
    return WSGIApplication()
