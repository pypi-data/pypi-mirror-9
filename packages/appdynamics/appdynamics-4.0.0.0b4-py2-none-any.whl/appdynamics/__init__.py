import logging
import os.path

from appdynamics.lib import default_log_formatter, running_tests

# The following is a very basic logging config which outputs WARNING level logs to stderr.
try:
    if not running_tests():
        logger = logging.getLogger('appdynamics')
        level = logging.WARNING
        logger.setLevel(level)
        logger.propagate = False
        handler = logging.StreamHandler()
        handler.setFormatter(default_log_formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
except:
    pass


def get_version(build_file=None):
    try:
        version = []

        if build_file is None:
            build_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'BUILD.txt')

        with open(build_file, 'r') as f:
            for line in f:
                version.append(line.strip().split('=')[-1])
    except:
        logging.getLogger('appdynamics.agent').exception("Couldn't parse build info.")
        return 'unknown'

    return ' '.join(version)
