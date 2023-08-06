from ..base import BaseInterceptor
from appdynamics.agent.models.errors import ErrorInfo

import logging


class LoggingInterceptor(BaseInterceptor):
    def __log(self, _log, logger, level, msg, args, **kwargs):
        with self.log_exceptions():
            if not logger.name.startswith('appdynamics'):
                bt = self.bt
                if bt:
                    display_name = '{name} [{level}]'.format(name=logger.name, level=logging.getLevelName(level))
                    error_info = ErrorInfo(msg % args, display_name, level)
                    if not self.agent.error_config_registry.is_error_ignored(error_info):
                        bt.add_error(error_info)
        _log(logger, level, msg, args, **kwargs)


def intercept_logging(agent, mod):
    LoggingInterceptor(agent, mod.Logger).attach('_log')
