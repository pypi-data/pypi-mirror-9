import re

from appdynamics.lib import parse_url, parse_qs
from appdynamics.agent.interceptor import dbapi


VENDOR = 'POSTGRESQL'
KV_RE = re.compile('\s*(?P<key>[a-zA-Z_]+)\s*=\s*(?P<remainder>.+)')


# For format of PostgreSQL connection strings, see:
# http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING


def parse_postgresql_url_dsn(dsn):
    url = parse_url(dsn, allow_fragments=False)

    if '?' in url.path:
        parts = url.path.split('?', 1)
        path, params = parts[0], parse_qs(parts[1])
    else:
        path = url.path
        params = parse_qs(url.query) if url.query else {}

    if 'host' in params:
        host = params['host'][0]
    else:
        host = url.hostname or 'localhost'

    if 'port' in params:
        port = params['port'][0]
    elif url.port:
        port = str(url.port)
    else:
        port = '5432'

    path = path.strip('/')

    if 'dbname' in params:
        dbname = params['dbname'][0]
    elif path:
        dbname = path
    elif 'user' in params:
        dbname = params['user'][0]
    else:
        dbname = url.username or 'postgres'

    return VENDOR, host, port, dbname


def parse_quoted_value(remainder):
    length = len(remainder)
    idx = 1

    start_idx = idx
    val = []

    while idx < length and remainder[idx] != "'":
        if remainder[idx:idx+2] in ("\\\\", "\\'"):
            # Valid escape sequence: collect the current run with the
            # escaped character, move past the escape sequence, and start a
            # new run.
            val.append(remainder[start_idx:idx] + remainder[idx + 1])
            idx += 2
            start_idx = idx
        else:
            idx += 1

    val.append(remainder[start_idx:idx])
    return ''.join(val), remainder[idx + 1:]


def parse_postgresql_kv_dsn(dsn):
    if "'" not in dsn:  # Fast path when there are no quoted strings.
        dsn = re.sub('(\s*=\s+|\s+=\s*)', '=', dsn).split()
        parts = dict(pair.split('=', 1) for pair in dsn)
    else:
        parts = {}
        m = KV_RE.match(dsn)

        while m:
            key, remainder = m.group('key'), m.group('remainder')

            if remainder[0] == "'":
                value, remainder = parse_quoted_value(remainder)
            else:
                split = remainder.split(None, 1)
                if len(split) == 1:
                    value, remainder = split[0], ''
                elif split:
                    value, remainder = split
                else:
                    break

            parts[key] = value
            m = KV_RE.match(remainder)

    return parse_postgresql_keyword_args(parts)


def parse_postgresql_keyword_args(parts):
    host = parts.get('host', 'localhost')
    port = parts.get('port', '5432')
    dbname = parts.get('dbname', parts.get('user', 'postgres'))
    return VENDOR, host, port, dbname


def parse_postgresql_dsn(dsn=None, *args, **kwargs):
    if dsn:
        if dsn.startswith('postgresql://'):
            return parse_postgresql_url_dsn(dsn)
        else:
            return parse_postgresql_kv_dsn(dsn)
    else:
        return parse_postgresql_keyword_args(kwargs)


def intercept_psycopg2(agent, mod):
    mod.connect = dbapi.make_connect_interceptor(agent, parse_postgresql_dsn, mod.connect)
