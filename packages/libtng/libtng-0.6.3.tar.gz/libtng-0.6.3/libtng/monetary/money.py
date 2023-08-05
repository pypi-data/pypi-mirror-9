import decimal
import operator


class Money(object):
    """Represents a monetary amount."""

    @property
    def amount(self):
        return self._amount

    @property
    def currency(self):
        return self._currency

    @property
    def rounded(self):
        """Returns the amount rounded to the currencies' minor
        unit."""
        return self._currency.round(self.amount)

    def __init__(self, amount, currency):
        """
        Initialize a new :class:`Monetary` object.

        Args:
            amount (decimal.Decimal): specifies the amount.
            currency (libtng.monetary.Currency): identifies the
                currency.
        """
        self._amount = decimal.Decimal(amount)
        self._currency = currency

    def __eq__(self, other):
        return isinstance(other, type(self))\
            and self.currency == other.currency

    def __repr__(self):
        return "{0} {1}".format(str(self._currency), self._amount)

    def __coerce_operands(self, other):
        allowed_types = (decimal.Decimal, int, str)
        if not isinstance(other, allowed_types):
            raise TypeError("unsupported operand type(s) for *: '{0}' and '{1}'"\
                .format(type(self).__name__, type(other).__name__))
        if isinstance(self, Money) and isinstance(other, Money)\
        and not (self.currency == other.currency):
            raise TypeError("cannot operate on monetary amounts of differend currencies.")
        return (
            self.amount if isinstance(self, Money) else decimal.Decimal(self),
            other.amount if isinstance(other, Money) else decimal.Decimal(other)
        )

    def __calculate(self, f, x, y):
        return Money(f(x, y), self._currency)

    def __add__(self, other):
        return self.__calculate(operator.add, *self.__coerce_operands(other))

    def __sub__(self, other):
        return self.__calculate(operator.sub, *self.__coerce_operands(other))

    def __mul__(self, other):
        return self.__calculate(operator.mul, *self.__coerce_operands(other))

    def __div__(self, other):
        return self.__calculate(operator.div, *self.__coerce_operands(other))