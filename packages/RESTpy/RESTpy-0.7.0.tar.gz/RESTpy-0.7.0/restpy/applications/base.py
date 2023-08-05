"""Base application objects which support hooks and exception handling.

Attributes:

    BaseApplication: The common base class for all WSGI applications in this
        package.
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from werkzeug.wrappers import BaseRequest
from werkzeug.wrappers import BaseResponse
from werkzeug.wrappers import Request


LOG = logging.getLogger(__name__)


class BaseApplication(object):

    """Base application which processes hooks and handles exceptions."""

    def __init__(self, before=(), after=(), request=None):
        """Initialize the application with some sequence of hooks.

        Args:
            before (iter of callable): An iterable of callables which are
                considered request hooks. Each of these will be executed before
                the handler and will be given the current request object. If
                a before hook returns a new request object it will replace the
                current request for the rest of the session.
            after (iter of callable): An iterable of callables which are
                considered response hooks. Each of these will be executed after
                the handler and will be given both the request and response. If
                the hook returns a new response object it will replace the
                current response for the rest of the session.
            request (BaseRequest, optional): Some subclass of the
                werkzeug.wrappers.BaseRequest which should be used to process
                new requests. If None is given the default value is the
                werkzeug.wrappers.Request class.
        """
        self._before = tuple(before)
        self._after = tuple(after)
        self._request = request or Request

    def before(self, request):
        """Execute the before hooks and return the final request object.

        Args:
            request (BaseRequest): The request object to process through the
                before hooks.

        Returns:
            BaseRequest: Some request object which should be used for the
                remainder of the request session.
        """
        for hook in self._before:

            result = hook(request)
            if isinstance(result, BaseRequest):

                request = result

        return request

    def after(self, request, response):
        """Execute the after hooks and return the final response object.

        Args:
            request (BaseRequest): The request object to process through the
                after hooks.
            response (BaseResponse): The response object to process through the
                after hooks.

        Returns:
            BaseResponse: Some response object which should be used when
                responding from the WSGI service.
        """
        for hook in self._after:

            result = hook(request, response)
            if isinstance(result, BaseResponse):

                response = result

        return response

    def route(self, request):
        """Get an endpoint and kwargs based on the request.

        Args:
            request (BaseRequest): The request object to route.

        Returns:
            tuple: A tuple containing the routing endpoint and any keyword
                arguments which should be passed to the endpoint upon
                execution.

        Note:
            The returned endpoint must be an implementation of the Endpoint
            interface defined elsewhere in this package.
        """
        raise NotImplementedError()

    def __call__(self, environ, start_response):
        """Execute the request and start the WSGI response."""
        try:

            try:

                request = self._request(environ)
                request = self.before(request)
                endpoint, endpoint_kwargs = self.route(request)
                response = endpoint.dispatch(request, **endpoint_kwargs)

            except HTTPException as exc:

                response = exc

            try:

                response = self.after(request, response)

            except HTTPException as exc:

                response = exc

            return response(environ, start_response)

        except Exception:

            LOG.exception("There was an unhandled exception in the request.")
            return InternalServerError()(environ, start_response)


__all__ = ('BaseApplication',)
