import libtng.exceptions


class ConnectionDoesNotExist(libtng.exceptions.ResourceDoesNotExist):
    """
    Should be raised when a database connection is request for a
    non-existing alias.
    """
    pass


class ConnectionAlreadyExists(libtng.exceptions.DuplicateResource):
    pass