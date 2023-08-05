import collections

from libtng import ipaddress
from libtng.datastructures import OrderedSet


class Hostname(object):
    """
    Maps a hostname to an IP address.
    """

    @property
    def hostname(self):
        return self._hostname

    @property
    def ip_address(self):
        return self._ip_address

    def __init__(self, hostname, ip_address):
        self._hostname = hostname
        self._ip_address = ipaddress.ip_address(ip_address)

    def __hash__(self):
        return hash(tuple(self))

    def __iter__(self):
        return iter((self._hostname, self._ip_address))

    def __repr__(self):
        return "Hostname('{0}','{1}')".format(*self)


class HostnameCollection(collections.MutableSet):

    def __init__(self, initial=None):
        initial = initial or []
        self._hostnames = {x.hostname for x in initial}
        self._addresses = {x.ip_address for x in initial}

    def add(self, hostname):
        self._hostnames[hostname.hostname] = hostname
        self._addresses[hostname.ip_address] = hostname