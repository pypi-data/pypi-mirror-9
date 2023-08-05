from libtng.monetary.currency import Currency
from libtng.monetary.exceptions import CurrencyAlreadyMapped
from libtng.monetary.exceptions import CurrencyDoesNotExist


class CurrencyProvider(object):
    """A registry for currencies."""

    def __init__(self):
        self.__registry = {}

    def populate(self, currencies):
        """
        Load currencies into the provied.

        Args:
            currencies: a list of tuples specifying the currencies.
        """
        map(self._fromtuple, currencies)

    def _fromtuple(self, obj):
        return self.add(*obj)

    def _fromdict(self, obj):
        return self.add(**obj)

    def add(self, name, code, minor_unit, valid_from, valid_to, override=False):
        """
        Add a new currency to the registry.

        Args:
            name (str): the name of the currency.
            code (str): the ISO 4217 code identifying the currency.
            minor_unit (int): specifies the decimal precision of the
                currency.
            valid_from (datetime.date): the date from which the currency
                is used.
            valid_to (datetime.date): the date to which the currency
                was used.

        Kwargs:
            override: a boolean indicating if existing currency mappings may
                be overridden.

        Returns:
            None
        """
        if code in self.__registry and not override:
            raise CurrencyAlreadyMapped(code=code)
        self.__registry[code] = Currency(code, minor_unit)

    def get(self, code):
        """Return a :class:`libtng.monetary.Currency` object
        specified by `code`.

        Args:
            code (str): an ISO 4217 code identifying the currency.

        Returns:
            libtng.monetary.Currency

        Raises:
            CurrencyDoesNotExist: the code is invalid.
        """
        try:
            return self.__registry[code]
        except KeyError as e:
            raise CurrencyDoesNotExist(*e.args)



provider = CurrencyProvider()