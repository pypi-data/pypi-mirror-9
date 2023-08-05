import json
import logging

from beaker.container import NamespaceManager, Container
from beaker.synchronization import file_synchronizer
from beaker.util import verify_directory
from beaker.exceptions import MissingCacheParameter, InvalidCacheBackendError

try:
    import cPickle as pickle
except:
    import pickle

try:
    from redis import StrictRedis, ConnectionPool
except ImportError:
    raise InvalidCacheBackendError("Redis cache backend requires the 'redis' library")

log = logging.getLogger(__name__)


class RedisManager(NamespaceManager):
    connection_pools = {}

    def __init__(self,
                 namespace,
                 url=None,
                 data_dir=None,
                 lock_dir=None,
                 expire=None,
                 **params):
        self.db = params.pop('db', None)
        self.dbpass = params.pop('password', None)

        NamespaceManager.__init__(self, namespace)
        if not url:
            raise MissingCacheParameter("url is required")

        if lock_dir:
            self.lock_dir = lock_dir
        elif data_dir:
            self.lock_dir = data_dir + "/container_tcd_lock"
        if hasattr(self, 'lock_dir'):
            verify_directory(self.lock_dir)

        # Specify the serializer to use (pickle or json?)
        self.serializer = params.pop('serializer', 'pickle')

        self._expiretime = int(expire) if expire else None

        conn_params = {}
        parts = url.split('?', 1)
        url = parts[0]
        if len(parts) > 1:
            conn_params = dict(p.split('=', 1) for p in parts[1].split('&'))

        host, port = url.split(':', 1)

        self.open_connection(host, int(port), **conn_params)

    def open_connection(self, host, port, **params):
        pool_key = self._format_pool_key(host, port)
        if pool_key not in self.connection_pools:
            self.connection_pools[pool_key] = ConnectionPool(host=host,
                                                             port=port,
                                                             db=self.db,
                                                             password=self.dbpass)
        self.db_conn = StrictRedis(connection_pool=self.connection_pools[pool_key],
                                   **params)

    def get_creation_lock(self, key):
        return file_synchronizer(identifier="tccontainer/funclock/%s" % self.namespace,
                                 lock_dir=self.lock_dir)

    def __getitem__(self, key):
        if self.serializer == 'json':
            payload = self.db_conn.get(self._format_key(key))
            if isinstance(payload, bytes):
                return json.loads(payload.decode('utf-8'))
            else:
                return json.loads(payload)
        else:
            return pickle.loads(self.db_conn.get(self._format_key(key)))

    def __contains__(self, key):
        return self.db_conn.exists(self._format_key(key))

    def has_key(self, key):
        return key in self

    def set_value(self, key, value, expiretime=None):
        key = self._format_key(key)

        #
        # beaker.container.Value.set_value calls NamespaceManager.set_value
        # however it (until version 1.6.4) never sets expiretime param.
        #
        # Checking "type(value) is tuple" is a compromise
        # because Manager class can be instantiated outside container.py (See: session.py)
        #
        if (expiretime is None) and (type(value) is tuple):
            expiretime = value[1]

        if self.serializer == 'json':
            serialized_value = json.dumps(value, ensure_ascii=True)
        else:
            serialized_value = pickle.dumps(value, 2)

        if expiretime:
            self.db_conn.setex(key, expiretime, serialized_value)
        else:
            self.db_conn.set(key, serialized_value)

    def __setitem__(self, key, value):
        self.set_value(key, value, self._expiretime)

    def __delitem__(self, key):
        self.db_conn.delete(self._format_key(key))

    def _format_key(self, key):
        return 'beaker:{0}:{1}'.format(self.namespace, key.replace(' ', '\302\267'))

    def _format_pool_key(self, host, port):
        return '{0}:{1}:{2}'.format(host, port, self.db)

    def do_remove(self):
        self.db_conn.flushdb()

    def keys(self):
        return self.db_conn.keys('beaker:{0}:*'.format(self.namespace))


class RedisContainer(Container):
    namespace_class = RedisManager
