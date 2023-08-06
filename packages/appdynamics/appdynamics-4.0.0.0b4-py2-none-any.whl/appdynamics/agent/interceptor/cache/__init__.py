from appdynamics.agent.models.exitcalls import EXIT_CACHE
from appdynamics.agent.interceptor.base import ExitCallInterceptor


class CacheInterceptor(ExitCallInterceptor):
    """Base class for cache interceptors.

    Extra Parameters
    -----------------
    cache_name : string
        The vendor name of this cache backend e.g. MEMCACHED.

    Required properties for `get_backend`
    -------------------------------------
        server_pool - a list of 'host:port' strings.

    """

    def __init__(self, agent, cls, cache_name):
        self.cache_name = cache_name
        super(CacheInterceptor, self).__init__(agent, cls)

    def get_backend(self):
        server_pool = map(str, self['server_pool'])

        identifying_properties = {
            'Vendor': self.cache_name,
            'Server Pool': '\n'.join(server_pool),
        }

        # All of the agents take the last server in the pool; not sure why.
        display_name = "{server_pool} - {vendor}".format(vendor=self.cache_name, server_pool=server_pool[-1])
        return self.agent.backend_registry.get_backend(EXIT_CACHE, identifying_properties, display_name)

from .redis import intercept_redis
from .memcache import intercept_memcache

__all__ = ['intercept_redis', 'intercept_memcache']
