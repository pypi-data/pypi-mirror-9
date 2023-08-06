from appdynamics.agent.interceptor.cache import CacheInterceptor


class MemcacheClientInterceptor(CacheInterceptor):
    def __init__(self, agent, cls):
        super(MemcacheClientInterceptor, self).__init__(agent, cls, 'MEMCACHED')

    def run_command(self, command_func, client, *args, **kwargs):
        with self.log_exceptions():
            self['server_pool'] = [':'.join(map(str, server.address)) for server in client.servers]
            self.start_exit_call(operation=command_func.__name__)

        result = command_func(client, *args, **kwargs)
        self.end_exit_call()
        return result


def intercept_memcache(agent, mod):
    interceptor = MemcacheClientInterceptor(agent, mod.Client)
    interceptor.attach([
        'set',
        'set_multi',
        'add',
        'replace',
        'append',
        'prepend',
        'cas',
        'get',
        'get_multi',
        'gets',
        'delete',
        'delete_multi',
        'incr',
        'decr',
        'flush_all',
    ], patched_method_name='run_command')
