import collections

import requests

from libtng.datastructures import OrderedSet
from libtng.sil.const import INDEX_URL
from libtng import six


class LanguageIndex(object):
    """
    In ISO 639-2, there are multiple name forms for some identified
    languages. The ISO 639-3 code tables now include a language
    name index with multiple names associated many code elements
    (primarily in English forms or variant anglicized spellings of
    indigenous names). The reference name from
    :attr:`Language.inverted_name` of the main table is included
    as an entry in this table, thus every code element has at least
    one row occurrence in the Language Names Index table. The  name
    appears in two forms, a "print" form used in most contexts,
    and an inverted form which fronts a language name root, e.g.,
    "Isthmus Zapotec" and "Zapotec, Isthmus". Where there is no root
    part to the name, the *Print_Name* and the *Inverted_Name* contain
    identical strings.
    """
    _dto = collections.namedtuple('LanguageIndex', ['identifier','print_name','inverted_name'])

    @classmethod
    def fromline(cls, line):
        return cls(*line)

    def __init__(self, identifier, print_name, inverted_name):
        """
        Initializes a new :class:`LanguageIndex` instance.

        Args:
            identifier: the ISO 639-3 identifier.
            print_name: One of the names associated with this identifier.
            inverted_name: reference language name.
        """
        self.identifier = identifier
        if not isinstance(print_name, six.text_type):
            print_name = print_name.decode('utf8')
        if not isinstance(inverted_name, six.text_type):
            inverted_name = inverted_name.decode('utf8')
        self.print_name = print_name
        self.inverted_name = inverted_name

    def as_tuple(self):
        return self._dto(identifier=self.identifier, print_name=self.print_name,
            inverted_name=self.inverted_name)

    def __hash__(self):
        return hash((self.identifier, self.inverted_name))


class LanguageIndexCollection(OrderedSet):

    @classmethod
    def fromsil(cls):
        response = requests.get(INDEX_URL).text.encode('utf8').split('\r\n')[1:]
        lines = [x for x in map(lambda x: x.split('\t') if x else None, response) if x]
        return cls(map(LanguageIndex.fromline, lines))