from .base import HttpException
from .notfound import NotFound
from .unauthorized import Unauthorized
from .servicenotavailable import ServiceNotAvailable
from .notallowed import RequestMethodNotAllowed
from .internalservererror import InternalServerError
from .badrequest import BadRequest
from .unprocessableentity import UnprocessableEntity

import warnings


warnings.warn("The libtng.exceptions.http module is deprecated, use libtng.http.exceptions instead.",
    DeprecationWarning, stacklevel=2)