import sqlalchemy.types as types


class IPAddress(types.TypeDecorator):
    """
    Coerces :class:`~libtng.ipaddress.IPv4Address` or
    :class:`~libtng.ipaddress.IPv6Address` to string.
    """

    impl = types.String


    def process_bind_param(self, value, dialect):
        return str(value) if value else None

    def process_result_value(self, value, dialect):
        return value

    def copy(self):
        return IPAddress(self.impl.length)