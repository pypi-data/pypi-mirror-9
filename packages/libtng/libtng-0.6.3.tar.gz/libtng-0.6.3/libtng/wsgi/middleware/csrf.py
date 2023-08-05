from libtng.wsgi.middleware.base import Middleware


REASON_NO_REFERER       = "Referer checking failed - no Referer."
REASON_BAD_REFERER      = "Referer checking failed - {0} does not match {1}."
REASON_NO_CSRF_COOKIE   = "CSRF cookie not set."
REASON_BAD_TOKEN        = "CSRF token missing or incorrect."

# Settings for CSRF cookie.
CSRF_KEY_LENGTH         = 32
CSRF_COOKIE_NAME        = 'csrftoken'
CSRF_COOKIE_AGE         = 60 * 60 * 24 * 7 * 52
CSRF_COOKIE_DOMAIN      = None
CSRF_COOKIE_PATH        = '/'
CSRF_COOKIE_SECURE      = False
CSRF_COOKIE_HTTPONLY    = False

# Dotted path to callable to be used as view when a request is
# rejected by the CSRF middleware.
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'



class CsrfProtectionService(object):

    def __init__(self, key_length=CSRF_KEY_LENGTH, cookie_name=CSRF_COOKIE_NAME,
        cookie_age=CSRF_COOKIE_AGE, cookie_domain=CSRF_COOKIE_DOMAIN,
        cookie_path=CSRF_COOKIE_PATH, cookie_secure=CSRF_COOKIE_SECURE,
        cookie_httponly=CSRF_COOKIE_HTTPONLY):
        """
        Initialize a new :class:`CsrfProtectionService` instance.

        Kwargs:
            key_length: an unsigned integer specifying the key length of
                the CSRF token.
            cookie_name: a string specifying the name of the CSRF cookie
                set at the client.
            cookie_age: an unsigned integer indicating the maximum age
                of the CSRF cookie, in seconds.
            cookie_domain: a string specifying the cookie domain; may be
                ``None``.
            cookie_path: a string specifying the path for which the cookie
                is set. Default is ``'/'``.
            cookie_secure: a boolean indicating if the cookie should be
                signed.
            cookie_httponly: a boolean indicating if the cookie is only used
                for HTTP.
        """
        self._key_length = key_length
        self._cookie_name = cookie_name
        self._cookie_age = cookie_age
        self._cookie_domain = cookie_domain
        self._cookie_path = cookie_path
        self._cookie_secure = cookie_secure
        self._cookie_httponly = cookie_httponly

    def process_response(self, request, response):
        """
        Process the outgoing response.

        Args:
            request: a :class:`libtng.wsgi.Request` instance
                representing the incoming request.
            reponse: a :class:`libtng.http.Response` instance
                representing the outgoing response.

        Returns:
            Response: the possibly modified `response`.
        """
        if getattr(response, 'csrf_processing_done', False):
            return response

        # If CSRF_COOKIE is unset, then :meth:`CsrfViewMiddleware.process_view`
        # was never called, probably because a request middleware returned
        # a response (for example, a redirect to a login page).
        if request.cookies.get("CSRF_COOKIE") is None:
            return response

        if not request.cookies.get("CSRF_COOKIE_USED", False):
            return response

        # Set the CSRF cookie even if it's already set, so we renew
        # the expiry timer.
        response.set_cookie(
            self._cookie_name,
            request.cookies["CSRF_COOKIE"],
            max_age=self._cookie_age,
            domain=self._cookie_domain,
            path=self._cookie_path,
            secure=self._cookie_secure,
            httponly=self._cookie_httponly
        )
        # Content varies with the CSRF cookie, so set the Vary header.
        patch_vary_headers(response, ('Cookie',))
        response.csrf_processing_done = True
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Middle to execute prior to calling a controller/view.

        Args:
            request: a :class:`libtng.wsgi.Request` instance
                representing the incoming request.
            callback: the controller callback function.
            callback_args: arguments passed to the callback function; always
                ``None`` when not using Django.
            callback_kwargs: parameters parsed from the request URL.

        Returns:
            None: the request-response cycle should continue as normal.
            Response: a :class:`libtng.http.Response` instance representing
                the response that will immediately be returned to the client.
        """
        if getattr(request, 'csrf_processing_done', False):
            return None

        try:
            csrf_token = _sanitize_token(request.cookies[CSRF_COOKIE_NAME])
            # Use same token next time
            request.META['CSRF_COOKIE'] = csrf_token
        except KeyError:
            csrf_token = None
            # Generate token and store it in the request, so it's
            # available to the view.
            request.META["CSRF_COOKIE"] = _get_new_csrf_key()

        # Wait until request.META["CSRF_COOKIE"] has been manipulated before
        # bailing out, so that get_token still works
        if getattr(callback, 'csrf_exempt', False):
            return None

        # Assume that anything not defined as 'safe' by RFC2616 needs protection
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                # Mechanism to turn off CSRF checks for test suite.
                # It comes after the creation of CSRF cookies, so that
                # everything else continues to work exactly the same
                # (e.g. cookies are sent, etc.), but before any
                # branches that call reject().
                return self._accept(request)

            if request.is_secure():
                # Suppose user visits http://example.com/
                # An active network attacker (man-in-the-middle, MITM) sends a
                # POST form that targets https://example.com/detonate-bomb/ and
                # submits it via JavaScript.
                #
                # The attacker will need to provide a CSRF cookie and token, but
                # that's no problem for a MITM and the session-independent
                # nonce we're using. So the MITM can circumvent the CSRF
                # protection. This is true for any HTTP connection, but anyone
                # using HTTPS expects better! For this reason, for
                # https://example.com/ we need additional protection that treats
                # http://example.com/ as completely untrusted. Under HTTPS,
                # Barth et al. found that the Referer header is missing for
                # same-domain requests in only about 0.2% of cases or less, so
                # we can use strict Referer checking.
                referer = request.referrer
                if referer is None:
                    return self._reject(request, REASON_NO_REFERER)

                # Note that request.get_host() includes the port.
                good_referer = 'https://%s/' % request.get_host()
                if not same_origin(referer, good_referer):
                    reason = REASON_BAD_REFERER % (referer, good_referer)
                    return self._reject(request, reason)

            if csrf_token is None:
                # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
                # and in this way we can avoid all CSRF attacks, including login
                # CSRF.
                return self._reject(request, REASON_NO_CSRF_COOKIE)

            # Check non-cookie token for match.
            request_csrf_token = ""
            if request.method == "POST":
                request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')

            if request_csrf_token == "":
                # Fall back to X-CSRFToken, to make things easier for AJAX,
                # and possible for PUT/DELETE.
                request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

            if not constant_time_compare(request_csrf_token, csrf_token):
                return self._reject(request, REASON_BAD_TOKEN)

        return self._accept(request)

    def process_response(self, request, response):
        """
        Process the outgoing response.

        Args:
            request: a :class:`libtng.wsgi.Request` instance
                representing the incoming request.
            reponse: a :class:`libtng.http.Response` instance
                representing the outgoing response.

        Returns:
            Response: the possibly modified `response`.
        """
        if getattr(response, 'csrf_processing_done', False):
            return response

        # If CSRF_COOKIE is unset, then :meth:`CsrfViewMiddleware.process_view`
        # was never called, probably because a request middleware returned
        # a response (for example, a redirect to a login page).
        if request.cookies.get("CSRF_COOKIE") is None:
            return response

        if not request.cookies.get("CSRF_COOKIE_USED", False):
            return response

        # Set the CSRF cookie even if it's already set, so we renew
        # the expiry timer.
        response.set_cookie(
            CSRF_COOKIE_NAME,
            request.cookies["CSRF_COOKIE"],
            max_age=CSRF_COOKIE_AGE,
            domain=CSRF_COOKIE_DOMAIN,
            path=CSRF_COOKIE_PATH,
            secure=CSRF_COOKIE_SECURE,
            httponly=CSRF_COOKIE_HTTPONLY
        )
        # Content varies with the CSRF cookie, so set the Vary header.
        patch_vary_headers(response, ('Cookie',))
        response.csrf_processing_done = True
        return response