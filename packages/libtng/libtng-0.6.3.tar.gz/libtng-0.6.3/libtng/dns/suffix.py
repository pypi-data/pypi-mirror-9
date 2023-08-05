"""
Downloads an queries the Public Suffix List (https://publicsuffix.org/).
"""
from encodings import idna
from urllib.request import urlopen
import sys
import re


__all__ = [
    'get_valid_tlds'
]


ICANN_TLD_LIST  = "http://data.iana.org/TLD/tlds-alpha-by-domain.txt"
PUBLIC_SUFFIX_LIST = "http://mxr.mozilla.org/mozilla-central/source/netwerk/dns/effective_tld_names.dat?raw=1"
LINESEP = '\n'
ICANN_TOKENS    = ("// ===BEGIN ICANN DOMAINS===", "// ===END ICANN DOMAINS===")
PRIVATE_TOKENS  = ("// ===BEGIN PRIVATE DOMAINS===", "// ===END PRIVATE DOMAINS===")
_valid = lambda x: not x.startswith('//') and x
_clean = lambda x: re.sub('^(\*\!)\.', '', x)

def _get_list():
    return urlopen(PUBLIC_SUFFIX_LIST).read()

def _get_icann_index(raw_data):
    start_token, stop_token = ICANN_TOKENS
    return (
        raw_data.find(start_token),
        raw_data.find(stop_token)
    )


def _get_private_index(raw_data):
    start_token, stop_token = PRIVATE_TOKENS
    return (
        raw_data.find(start_token),
        raw_data.find(stop_token)
    )


def _download():
    raw_data = _get_list()
    icann, private = (
        raw_data[slice(*_get_icann_index(raw_data))],
        raw_data[slice(*_get_private_index(raw_data))]
    )
    assert icann.startswith(ICANN_TOKENS)
    assert private.startswith(PRIVATE_TOKENS)
    return icann, private


def _getlines(raw_data):
    return [x for x in raw_data.splitlines() if (_valid(x))]


def get_public_suffixes(with_private=False, normalize=True):
    """
    Return a list containing all valid top-level domain names
    and their extensions.

    :param with_private:
        indicates if private extensions should be included in the
        list. Default is ``False``.
    :param normalize:
        indicates if internationalized domain names (IDN) should be
        normalized to ASCII. Default is ``True``.
    :returns:
        a :class:`list` of :class:`str` instances.
    """
    raise NotImplementedError


def get_valid_tlds():
    """
    Return a list containing all valid top-level domain
    names.
    """
    raw_data = urlopen(ICANN_TLD_LIST).read().decode()
    return [x.lower() for x in raw_data.splitlines()
        if (not x.startswith('#') and x)]
