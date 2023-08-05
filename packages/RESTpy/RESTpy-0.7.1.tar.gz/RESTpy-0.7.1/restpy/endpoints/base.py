"""Base endpoints which provide handler functionality."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug import exceptions


class Endpoint(object):

    """A REST service endpoint which implements request handling functions.

    Endpoint implementation are welcome to subclass this definition. The
    minimum definition of any Endpoint must contain a 'dispatch()' method
    which takes a request and keyword arguments. In this implementation,
    the dispatch method will look for a method named after the HTTP method
    in use (get, post, etc.). Method names must be lower case.

    If a method is not found a MethodNotAllowed exception is thrown.
    """

    def head(self, request, **kwargs):
        """Execute GET and chop off the body content."""
        response = self._method_or_raise('get')(request, **kwargs)
        response.set_data('')
        return response

    def _allowed_methods(self):
        """Generate a list of supported methods for the endpoint."""
        methods = [
            method for method in dir(self)
            if not method.startswith('_') and
            method != 'dispatch'
        ]
        # Pluck head if there is not defined get since head requires get.
        if 'head' in methods and 'get' not in methods:

            methods.remove('head')

        return methods

    def _method_or_raise(self, method):
        """Get a method if defined or raise MethodNotAllowed."""
        if not hasattr(self, method):

            raise exceptions.MethodNotAllowed(
                valid_methods=self._allowed_methods(),
            )

        return getattr(self, method)

    def dispatch(self, request, **kwargs):
        """Route the request to the appropriate handler."""
        verb = request.method.lower()
        return self._method_or_raise(verb)(request, **kwargs)


__all__ = ('Endpoint',)
