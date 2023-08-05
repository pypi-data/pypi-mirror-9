


class BasicAuthentication(object):
    """
    Maps the 'public' and 'private' parts of an
    HTTP Basic Authorization header to the specified
    values.
    """

    def __init__(self, public, private):
        self.public = public
        self.private = private

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass