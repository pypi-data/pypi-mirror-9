"""Easy import module for common RESTpy features."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug.routing import Map

from .applications.base import BaseApplication
from .applications.map import MapApplication
from .applications.map import MapPluginApplication
from .endpoints.base import Endpoint
from .hooks.after.context import context_clear
from .hooks.before.unique import unique_request
from .middlewares.context import ContextClearMiddleware
from .middlewares.unique import UniqueEnvironMiddleware
from .middlewares.unique import RequestLogger


class Application(BaseApplication):

    """Application object which chooses the appropriate implementation."""

    def __new__(cls, *args, **kwargs):
        """Return a MapApplication or MapPluginApplication."""
        first_arg = (
            kwargs.get('routes', None) or
            kwargs.get('plugins', None) or
            args[0]
        )

        if isinstance(first_arg, Map):

            return MapApplication(*args, **kwargs)

        if (
                hasattr(first_arg, '__iter__') or
                hasattr(first_arg, 'next') or
                hasattr(first_arg, '__next__')
        ):

            return MapPluginApplication(*args, **kwargs)

        raise ValueError(
            'Could not determine application type from parameters.'
        )

__all__ = (
    'Application',
    'BaseApplication',
    'MapApplication',
    'MapPluginApplication',
    'Endpoint',
    'context_clear',
    'unique_request',
    'ContextClearMiddleware',
    'UniqueEnvironMiddleware',
    'RequestLogger',
)
