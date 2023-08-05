import collections

from libtng import six
from libtng import module_loading

from libtng.http.exceptions import AuthorizationHeaderParseError
from libtng.http.exceptions import UnknownAuthorizationScheme


BasicAuth = collections.namedtuple('BasicAuth', ['public','private'])


class AuthorizationSchemeRegistry(object):

    def __init__(self):
        self._schemes = {
            'Basic': lambda x: BasicAuth(**dict(zip(['public','private'],
                x.decode('base64').split(':'))))
        }

    def parse(self, header):
        """
        Parses an ``Authorization`` header and returns a
        dictionary holding the values.

        Args:
            header (str): the content of an ``Authorization``
                header as specified on an incoming HTTP
                request.

        Returns:
            namedtuple
        """
        try:
            scheme_name, content = map(lambda x: x.strip(),
                header.strip().split(' ', 1))
            values = self.get_scheme_parser(scheme_name)(content)
        except UnknownAuthorizationScheme:
            raise
        except Exception:
            raise AuthorizationHeaderParseError
        return values

    def add(self, scheme_name, parser):
        """
        Add a new authorization scheme to the registry. Specify a
        name and parser. The parser takes the content of the
        ``Authorization`` header as it's single argument and must
        return a namedtuple holding the values parsed from the
        header.

        Args:
            scheme_name (str): specifies a name identifying the
                authorization scheme.
            parser: a callable or string specifying the parser.
                Takes the ``Authorization`` header content as
                it's single argument. If `parser` is a string,
                it is imported and instantiated (a class is
                assumed).

        Returns:
            None
        """
        if isinstance(parser, six.string_types):
            parser = module_loading.import_string(parser)
        self._schemes[scheme_name] = parser

    def get_scheme_parser(self, scheme_name):
        """
        Return a HTTP ``Authorization`` header parser identified
        by `scheme_name`.
        """
        try:
            return self._schemes[scheme_name]
        except KeyError:
            raise UnknownAuthorizationScheme