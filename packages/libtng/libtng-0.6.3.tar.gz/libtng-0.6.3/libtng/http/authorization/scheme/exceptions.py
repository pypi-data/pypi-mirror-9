


class SchemeAlreadyRegistered(Exception):

    def __init__(self, scheme_name):
        self.scheme_name = scheme_name


class SchemeDoesNotExist(LookupError):
    pass