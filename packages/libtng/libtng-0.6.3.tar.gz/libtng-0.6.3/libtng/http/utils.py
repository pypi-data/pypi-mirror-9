import re
import collections

from libtng.hashers import sign_message


header_pattern = re.compile('(\w+)[:=] ?"?([\w\s\d\.\-\_\:]+)"?')


def parse_authorization_header(header):
    """
    Parses an HTTP 1.1 Authorization header according to the
    RFC 2617 specification.

    Args:
        header: a string containing the contents of the
            Authorization header of a request.

    Returns:
        tuple: containing a string specifying the authorization
            realm, and a dictionary holding the parameters.

    Raises:
        ValueError: missing protocol indicator in header.
    """
    m = re.match('^(?P<protocol>\w+)', header)
    if not m:
        raise ValueError("Missing protocol indicator in Authorization header.")
    params = collections.OrderedDict(header_pattern.findall(header))
    if not params:
        raise ValueError("No parameters specified.")
    return m.group('protocol'), params


def signed_authorization_header(protocol, client_identifier, private_key, payload, digestmod=None):
    """
    Generate the parameters of an HTTP 1.1 Authorization header
    using a private key and the request payload.

    Args:
        protocol: a string specifying the protocol name.
        client_identifier: a tuple containing the parameter name
            and value, identifying the system operator that issued
            the request.
        private_key: a string containing the private key.
        payload: a string containing the request body.

    Returns:
        tuple: containing a :class:`str` and a
            :class:`datetime.datetime`, holding the
            authentorization header parameters.
    """
    key, value = client_identifier
    signature, timestamp = sign_message(private_key, payload, digestmod=digestmod)
    return '{protocol} {0}="{1}" signature="{2}" timestamp="{3}"'\
        .format(key, value, signature, str(timestamp), protocol=protocol)

