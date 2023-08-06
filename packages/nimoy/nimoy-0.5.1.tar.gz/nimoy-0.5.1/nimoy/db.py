from importlib import import_module
from functools import partial


class DatabaseStructure(object):

    def __init__(self, name, backend_name=None, connection_str=None):
        self._backend = None
        self._lists = {}
        self.name = name
        if backend_name is not None:
            self.init_backend(backend_name, connection_str)

    def init_backend(self, backend_name, connection_str=None):
        backend_name = 'nimoy.backends.{}'.format(backend_name) if '.' not in backend_name else backend_name
        self._backend_module = import_module(backend_name)
        self._backend_cls = getattr(self._backend_module, 'DatabaseBackend')
        self._backend = self._backend_cls(self.name, connection_str)

    def close(self):
        if self._backend is not None:
            self._backend.close()

    def reset_backend(self, fixture_dict=None):
        if self._backend is not None:
            self._backend.reset(self)
            if fixture_dict is not None:
                return self.load_fixture(fixture_dict)

    def load_fixture(self, fixture_dict):
        if self._backend is not None:
            self._backend.load_fixture(self, fixture_dict)

    def add_list(self, name, name_plural, new_obj_fn, not_found_cls, **kw):
        self._lists[name] = {
            'name': name,
            'name_plural': name_plural,
            'new_obj_fn': new_obj_fn,
            'not_found_cls': not_found_cls,
        }
        self._lists[name].update(kw)

    def construct_functions(self, list_name):
        return [_construct_function(self, list_name, fn_name) for fn_name in ['create', 'update_one', 'update_many', 'get_one', 'get_many']]


def create_database_structure(name, backend_name=None, connection_str=None):
    return DatabaseStructure(name, backend_name, connection_str)


def _construct_function(db_struct, list_name, fn_name):
    def _fn(db_struct, list_name, fn_name, *args, **kw):
        if db_struct._backend is not None:
            backend_method = getattr(db_struct._backend, fn_name)
            return backend_method(db_struct, list_name, *args, **kw)
        else:
            raise BackendNotInitialized
    return partial(_fn, db_struct, list_name, fn_name)


class BackendNotInitialized(Exception):
    pass
