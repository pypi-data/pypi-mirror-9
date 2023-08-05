"""Response hooks related to the global request context."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ... import context


LOG = logging.getLogger(__name__)


def context_clear(request, response):
    """Clear the request context after a response is generated.

    This hook will clear the context.storage container for the current thread.
    This is intended to be run as the last hook in the stack. Only use this
    hook if you do not use WSGI middlewares. Some middlewares may require the
    context.storage container. If middlewares are in use consider using the
    ContextClearMiddleware also provided in this package.
    """
    LOG.debug('Request complete. Clearing context.')
    context.clear()


__all__ = ('context_clear',)
