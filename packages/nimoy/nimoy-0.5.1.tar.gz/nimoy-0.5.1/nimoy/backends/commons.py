class BaseDatabaseBackend(object):
    def __init__(self, name, connection_str=None):
        self.name = name
        self.connection_str = connection_str
        self._post_init()

    def _post_init():
        pass
