from .currencyprovider import provider
from .currency import Currency
from .money import Money



def money_factory(amount, currency_code):
    """Create a new monetary amount.

    Args:
        amount (decimal.Decimal): specifies the monetary amount.
        currency_code (str): an ISO 4217 code identifying the
            currency.

    Returns:
        libtng.monetary.Money
    """
    return Money(amount, provider.get(currency_code))


def get_currency(code):
    """Get a :class:`Currency` object identified by
    `code`.

    Args:
        code (str): an ISO 4217 code identifying the
            currency.

    Returns:
        Currency
    """
    return provider.get(code)


load_currencies = provider.populate
register_currency = provider.add