"""Middlewares related to thread local storage."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .. import context


LOG = logging.getLogger(__name__)


class ContextClearMiddleware(object):

    """Clear the context.storage after the request is finished."""

    def __init__(self, application):
        """Initialize the middleware with a wrapped application."""
        self.application = application

    def __call__(self, environ, start_response):
        """Clear the context.storage for this thread."""
        response = self.application(environ, start_response)
        LOG.debug('Request complete. Clearing context.')
        context.clear()
        return response


__all__ = ('ContextClearMiddleware',)
