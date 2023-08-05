import collections

import requests

from libtng.datastructures import OrderedSet
from libtng.sil.const import CODE_SET_URL
from libtng import six


class Language(object):
    """
    Represents a language in the ISO 639-3 code set.
    """
    _dto = collections.namedtuple('Language',['identifier','bibliographical','terminological',
        'part1','scope','language_type','reference_name','comment'])

    @classmethod
    def fromline(cls, line):
        return cls(*line)

    def __init__(self, identifier, bibliographical, terminological,
        part1, scope, language_type, reference_name, comment):
        """
        Initialize a new :class:`Language` instance.

        Args:
            identifier: the ISO 639-3 identifier.
            bibliographical: equivalent 639-2 identifier of the
                bibliographic applications  code set, if there is one.
            terminological: equivalent 639-2 identifier of the
                terminology applications code set, if there is one.
            part1: equivalent 639-1 identifier, if there is one.
            scope: I(ndividual), M(acrolanguage), S(pecial).
            language_type: A(ncient), C(onstructed),  E(xtinct),
                H(istorical), L(iving), S(pecial).
            reference_name: reference language name.
            comment: comment relating to one or more of the columns.
        """
        self.identifier = identifier
        self.bibliographical = bibliographical
        self.terminological = terminological
        self.part1 = part1
        self.scope = scope
        self.language_type = language_type
        if not isinstance(reference_name, six.text_type):
            reference_name = reference_name.decode('utf8')
        self.reference_name = reference_name
        self.comment = comment

    def as_tuple(self):
        return self._dto(identifier=self.identifier, bibliographical=self.bibliographical or None,
            terminological=self.terminological or None, part1=self.part1 or None, scope=self.scope,
            language_type=self.language_type, reference_name=self.reference_name,
            comment=self.comment or None)

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        try:
            return str(self) == str(other)
        except Exception:
            return False

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return "Language{0}".format((self.identifier, self.bibliographical,
            self.terminological, self.part1, self.scope, self.language_type,
            self.reference_name, self.comment))


class LanguageCollection(OrderedSet):

    @classmethod
    def fromsil(cls):
        response = requests.get(CODE_SET_URL).text.split('\r\n')[1:]
        lines = [x for x in map(lambda x: x.split('\t') if x else None, response) if x]
        return cls(map(Language.fromline, lines))