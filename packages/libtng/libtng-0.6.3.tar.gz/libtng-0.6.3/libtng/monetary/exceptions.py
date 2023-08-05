

class CurrencyAlreadyMapped(Exception):

    def __init__(self, code):
        self._code = code


class CurrencyDoesNotExist(KeyError):
    pass