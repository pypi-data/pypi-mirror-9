from appdynamics.agent.models.transactions import ENTRY_DJANGO
from appdynamics.agent.interceptor.frameworks.wsgi import WSGIInterceptor
from appdynamics.agent.interceptor.base import BaseInterceptor


class DjangoBaseHandlerInterceptor(BaseInterceptor):
    def _handle_uncaught_exception(self, handle_uncaught_exception, base_handler, request, resolver, exc_info):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*exc_info)

        return handle_uncaught_exception(base_handler, request, resolver, exc_info)


def intercept_django_wsgi_handler(agent, mod):
    WSGIInterceptor(agent, mod.WSGIHandler, ENTRY_DJANGO).attach('__call__', patched_method_name='application_callable')


def intercept_django_base_handler(agent, mod):
    DjangoBaseHandlerInterceptor(agent, mod.BaseHandler).attach('handle_uncaught_exception')
