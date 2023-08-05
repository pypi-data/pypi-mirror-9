import copy
import importlib

from libtng import timezone
from libtng.http.exceptions import Unauthorized
from libtng.http.exceptions import UnknownAuthorizationScheme
from libtng.http.exceptions import UnprocessableEntity
from libtng.http.views.generic.base import View


class RestView(View):
    SINGLETON   = 'Singleton'
    COLLECTION  = 'Collection'

    #: Specifies the resource type.
    resource_type = None
    authentication_required = True
    authenticate = None

    #: Projection to return when the request did not specify the
    #: ``Accept`` header.
    default_mimetype = "application/json"
    authorization_scheme = None

    #: A :class:`libtng.http.rest.Projector` subclass that can
    #: project the desired content types.
    projector = None
    limit = 25
    offset = 0
    overrides = {}

    #: Specifies the fields of the Data Transfer Object (DTO)
    #: that are exposed to the client.
    exposed_attrs = None

    #: Keyword arguments that must be parsed from the URL regex
    #: to identify a resource.
    ident_attrs = None

    def __init__(self, *args, **kwargs):
        self.mimetype = self.default_mimetype if not self.mimetype\
            else self.mimetype
        super(RestView, self).__init__(*args, **kwargs)

    def get_ident(self):
        """
        Returns the parameters specified on the incoming HTTP
        request that identify the resource.
        """
        return {x: self.kwargs[x] for x in (self.ident_attrs or [])}

    def get_predicate(self):
        """
        Returns the parameters specified on the incoming HTTP
        request that limit the result dataset.
        """
        predicate = self.get_default_predicate()
        return predicate

    def get_default_predicate(self):
        """
        Returns the default predicate used to limit the entities
        contained in a collection.
        """
        return {
            'until' : timezone.now(),
            'limit' : self.limit,
            'offset': self.offset
        }

    def get_singleton(self):
        return self.finder.get_by_params(**self.get_ident())\
            .serialize(self.get_exposed_attrs())

    def get_collection(self):
        return map(lambda x: x.serialize(self.get_exposed_attrs()),
            self.finder.list_by_predicate(**self.get_predicate()))

    def get_response_data(self):
        return self.get_singleton() if (self.resource_type == self.SINGLETON)\
            else self.get_collection()

    def authenticate_request(self, request):
        """
        Authenticates an incoming HTTP request. Since RESTful APIs
        are stateless, each request needs to be authenticated and
        authorized. These steps are implemented at the view level.

        In order to authenticate, the view must be constructed with
        the `authenticate` argument; a callable that takes
        a request object and performs the necessary operations to
        authenticate and authorize it. If authentication fails, it
        should return ``False``.
        """
        mimetype = self.get_projection_type()
        try:
            authorization = request.authorization
        except UnknownAuthorizationScheme:
            hint = "Unknown authentication scheme specified."
            detail = None
            if self.authorization_scheme:
                detail = "Allowed authentication schemes: {0}"\
                    .format(self.authorization_scheme)
            raise UnknownAuthorizationScheme(mimetype=mimetype, detail=detail,
                response_factory=self.render_to_response, hint=hint)
        except (ValueError, TypeError):
            hint = "Unable to parse the content of the Authorization header."
            raise UnprocessableEntity(mimetype=mimetype, hint=hint,
                response_factory=self.render_to_response)
        if not authorization or not request.ident.is_authenticated():
            headers = {}
            hint = None
            if authorization:
                hint = "Unable to authenticate using the credentials specified in the Authorization header."
            if self.authorization_scheme and not authorization:
                headers['WWW-Authenticate'] = self.authorization_scheme
            raise Unauthorized(response_factory=self.render_to_response,
                mimetype=mimetype, headers=headers, hint=hint)

    def get_response_headers(self):
        """
        Return a :class:`dict` specifying the headers of the outgoing
        HTTP response.
        """
        return {}

    def get_projection_type(self):
        """
        Returns the desired projection mimetype. ``Accept`` headers may
        contain multiple mimetypes, but :meth:`RestView.get_projection_type()`
        always returns the first one specified.
        """
        return self.request.accept_mimetypes[0][0]\
            if ('Accept' in self.request.headers)\
            else self.default_mimetype

    def project(self, mimetype, serialized):
        """
        Project the serialized resource to the output format.

        Args:
            mimetype (str): the mimetype to project to.
            serialized (dict): the serialized Data Transfer Object (DTO).

        Returns:
            str: output returned directly to the client.
        """
        return self.projector.project(mimetype, serialized)

    def render_to_response(self, context_data, status_code=200, mimetype=None,
        headers=None, content_type=None):
        mimetype = mimetype or self.get_projection_type()
        content, content_headers = self.project(mimetype, context_data)
        content_headers.update(headers or {})
        return self.response_factory(content + "\n", headers=content_headers,
            status=status_code, mimetype=mimetype)

    def dispatch(self, request, *args, **kwargs):
        # Parse the Accept header and assess if we can respond
        # with the specified content type.
        client_accepts = self.get_projection_type()
        if not self.projector.can_project(client_accepts):
            detail = "Available content-types: {0}"\
                .format(', '.join(self.projector.mimetypes))
            hint = "Unable to respond using content-type '{0}'"\
                .format(client_accepts)
            raise UnprocessableEntity(detail=detail, hint=hint,
                response_factory=self.render_to_response, mimetype=self.default_mimetype)

        if self.authentication_required:
            self.authenticate_request(request)
        return super(RestView, self).dispatch(request, *args, **kwargs)

    def get_exposed_attrs(self):
        """
        Get the publicly exposed attributes from the Data
        Transfer Object (DTO).

        Returns:
            tuple
        """
        return tuple(self.exposed_attrs or [])