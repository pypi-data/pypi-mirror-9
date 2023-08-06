from mongomock import Connection as MockConnection
from pymongo.mongo_client import MongoClient

from .commons import BaseDatabaseBackend


DEFAULT_LIMIT = 10000000


class DatabaseBackend(BaseDatabaseBackend):
    def _post_init(self):
        if self.connection_str.startswith('mongomock://'):
            self._connect_mongomock()
        else:
            self._connect_mongodb()

    def _connect_mongomock(self):
        self._connection = MockConnection()
        self._db = self._connection[self.name]

    def _connect_mongodb(self):
        self._connection = MongoClient(self.connection_str)
        self._db = self._connection[self.name]

    def load_fixture(self, st, fixture_dict):
        raise NotImplemented

    def create(self, st, list_name, *args, **kw):
        raise NotImplemented

    def update_one(self, st, list_name, _id, **kw):
        raise NotImplemented

    def update_many(self, st, list_name, _w, **kw):
        raise NotImplemented

    def get_one(self, st, list_name, _w):
        raise NotImplemented

    def get_many(self, st, list_name, _w, limit=DEFAULT_LIMIT, offset=0, order_by=('_id', 'desc')):
        raise NotImplemented
