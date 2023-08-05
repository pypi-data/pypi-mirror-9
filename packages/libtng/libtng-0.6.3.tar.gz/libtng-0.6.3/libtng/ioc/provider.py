


class Provider(object):
    """
    Registry holding all dependencies, features and specifications.
    """

    def __init__(self):
        self._features = {}

    def get(self, key):
        """
        Return a :class:`~libtng.ioc.Feature` identified by `key`.
        """
        return self._features[key]

    def provide(self, key, feature):
        """
        Inject a feature to provide that identifies itself by `key`.
        """
        self._features[key] = feature


_provider = Provider()
