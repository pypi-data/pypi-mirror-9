from psycopg2.extensions import register_adapter, AsIs

from libtng.ipaddress import IPv4Address
from libtng.ipaddress import IPv6Address

from base import BaseHandler


__all__ = ['ConnectionHandler']


class ConnectionHandler(BaseHandler):
    dsn_format          = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    default_port        = '5432'
    application_name    = 'postgresql'
    application_version = '9.3'

    @property
    def dsn(self):
        return self.get_dsn()

    def __init__(self, options):
        self.options = options

    def get_dsn(self):
        extra_params = {}
        return self.options.format_dsn(self.dsn_format, **extra_params)


def adapt_ip(ip_address):
    if ip_address is None:
        return AsIs('NULL')
    masklen = '/32' if (ip_address.version == 4) else '/128'
    return AsIs("'{0}{1}'::inet".format(str(ip_address), masklen))


register_adapter(IPv4Address, adapt_ip)
register_adapter(IPv6Address, adapt_ip)