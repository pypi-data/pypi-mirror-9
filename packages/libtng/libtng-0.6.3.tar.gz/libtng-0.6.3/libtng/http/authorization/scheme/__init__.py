"""
Specifies an API for parsing HTTP ``Authorization`` headers.
"""
from .registry import AuthorizationSchemeRegistry


_registry = AuthorizationSchemeRegistry()
parse_authorization_header = _registry.parse