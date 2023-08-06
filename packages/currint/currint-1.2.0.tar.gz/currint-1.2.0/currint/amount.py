from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


class Amount(object):
    """
    An amount of a currency.
    """

    def __init__(self, currency, value):
        """
        Initialises the Amount with a Currency object and an
        integer value of its minor unit (i.e. cents for USD)
        """
        assert isinstance(value, (int, long))
        assert not isinstance(currency, basestring)
        self.currency = currency
        self.value = value

    @classmethod
    def from_code_and_minor(cls, currency_code, value):
        """
        Initialises the amount with a currency code and an integer value
        of minor units
        """
        from .currency import currencies
        try:
            return cls(currencies[currency_code.upper()], value)
        except KeyError:
            raise ValueError("Invalid currency code %s" % currency_code)

    @classmethod
    def from_code_and_major(cls, currency_code, value):
        """
        Initialises the amount with a currency code and a value
        in the major unit (e.g. "1.43", Decimal("1.43"), 10)
        """
        from .currency import currencies
        try:
            currency = currencies[currency_code.upper()]
            return cls(currency, currency.major_to_minor(Decimal(value)))
        except KeyError:
            raise ValueError("Invalid currency code %s" % currency_code)
        except InvalidOperation:
            raise ValueError("Invalid currency value %s" % value)

    def __str__(self):
        return unicode(self).encode("utf8")

    def __unicode__(self):
        return self.currency.format(self.value)

    def __repr__(self):
        return "<Amount %s, %s>" % (self.currency, self.value)

    def __eq__(self, other):
        return (self.currency == other.currency) and (self.value == other.value)

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("You cannot add amounts of different currencies (%s and %s)" % (self.currency, other.currency))
        return Amount(self.currency, self.value + other.value)

    def __sub__(self, other):
        if self.currency != other.currency:
            raise ValueError("You cannot subtract amounts of different currencies (%s and %s)" % (self.currency, other.currency))
        return Amount(self.currency, self.value - other.value)

    def __nonzero__(self):
        return bool(self.value)

    def apply_factor(self, other):
        if not isinstance(other, (int, long, Decimal)):
            raise ValueError("You can only apply an integer, long or Decimal factor to an Amount")
        return Amount(
            self.currency,
            int(Decimal(self.value * other).to_integral(ROUND_HALF_UP)),
        )

    def to_major_decimal(self):
        "Returns our value as a Decimal of major units"
        return self.currency.minor_to_major(self.value)
