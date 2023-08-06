from appdynamics.agent.interceptor.cache import CacheInterceptor


class RedisConnectionInterceptor(CacheInterceptor):
    def __init__(self, agent, cls):
        super(RedisConnectionInterceptor, self).__init__(agent, cls, 'REDIS')

    def _send_packed_command(self, send_packed_command, connection, command):
        with self.log_exceptions():
            # 'dbname' is currently unused by other agents.
            # self['dbname'] = connection.db
            connection_class = type(connection).__name__
            if connection_class == 'UnixDomainSocketConnection':
                self['server_pool'] = [connection.path]
            else:
                self['server_pool'] = ['{host}:{port}'.format(host=connection.host, port=connection.port)]

            self.start_exit_call(operation=str(command))

        result = send_packed_command(connection, command)
        self.end_exit_call()
        return result


def intercept_redis(agent, mod):
    RedisConnectionInterceptor(agent, mod.Connection).attach('send_packed_command')
