"""Provides an interface to map URLs to Python functions."""
from libtng.urlprovider.iurlprovider import IUrlProvider
from libtng.urlprovider.notimplemented import MissingLibraryUrlProvider
try:
    from libtng.urlprovider._werkzeug import WerkzeugUrlProvider
except ImportError:
    WerkzeugUrlProvider = MissingLibraryUrlProvider.create_class('werkzeug',
        'WerkzeugUrlProvider')

