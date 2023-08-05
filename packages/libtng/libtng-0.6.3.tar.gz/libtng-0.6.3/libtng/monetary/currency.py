import decimal

from libtng import six


class Currency(object):
    """Represents a currency."""
    __slots__ = ['_iso','_precision']

    @property
    def iso(self):
        return self._iso

    @property
    def minimal_amount(self):
        x = '.' + ((self._precision - 1) * '0') + '1'
        return decimal.Decimal(x)

    def __init__(self, iso, precision):
        """
        Initialize a new :class:`Currency` object.

        Args:
            iso (str): the ISO 4217 code identifying the currency.
            precision (int): the decimal precision of the currency.
        """
        self._iso = iso
        self._precision = precision

    def round(self, amount):
        """
        Round the amount to the precision specified by the currencies'
        minor unit.

        Args:
            amount (decimal.Decimal): the monetary amount.

        Returns:
            decimal.Decimal
        """
        x = '.' + ((self._precision - 1) * '0') + '1'
        return decimal.Decimal(amount)\
            .quantize(decimal.Decimal(x), rounding=decimal.ROUND_HALF_UP)

    def __eq__(self, other):
        return isinstance(other, type(self)) \
            and self.iso == other.iso

    def __repr__(self):
        return "Currency('{0}', {1})".format(self._iso, self._precision)

    def __str__(self):
        return str(self._iso)

    def __unicode__(self):
        return six.text_type(self._iso)