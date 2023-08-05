"""
WSGI utilities.
"""
from libtng.wsgi.application import WSGIApplication
try:
    from libtng.wsgi.request import WSGIRequest
except ImportError:
    pass
