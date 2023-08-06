import sys
from .wsgi import WSGIInterceptor
from ..base import BaseInterceptor


class CherryPyHTTPErrorInterceptor(BaseInterceptor):
    def _set_response(self, set_response, *args, **kwargs):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*sys.exc_info())
        return set_response(*args, **kwargs)


def intercept_cherrypy(agent, mod):
    WSGIInterceptor(agent, mod.Application).attach('__call__', patched_method_name='application_callable')
    CherryPyHTTPErrorInterceptor(agent, mod.HTTPError).attach('set_response')
