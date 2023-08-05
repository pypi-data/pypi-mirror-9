"""Middlewares related to uniquely identifying a request."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import uuid

from .. import context


LOG = logging.getLogger(__name__)


class UniqueEnvironMiddleware(object):

    """Assign a UUID to the WSGI environ for tracking.

    This middleware will look for the header 'Request-Id'. If it exists the
    found value will be left alone. If it does not exist a new UUID4 will be
    generated and stored in that header.

    The new request id will also be attached to context storage under the
    attribute 'request_id'. This can be used for logging purposes if desired.
    """

    def __init__(self, application):
        """Initialize the middleware with a wrapped application."""
        self.application = application

    def __call__(self, environ, start_response):
        """Attach the UUID and run the wrapped application."""
        key = 'HTTP_REQUEST_ID'
        request_id = environ.setdefault(key, str(uuid.uuid4()))
        context.storage.request_id = request_id
        LOG.debug('Created unique request %s.', request_id)
        return self.application(environ, start_response)


class RequestLogger(logging.Logger):

    """Inject the unique request id into every log record."""

    def makeRecord(self, *args, **kwargs):
        """Create a record and attach the request_id."""
        record = super(RequestLogger, self).makeRecord(*args, **kwargs)
        record.request_id = (
            context.storage.request_id
            if hasattr(context.storage, 'request_id')
            else '00000000-0000-0000-0000-000000000000'
        )
        return record


__all__ = ('UniqueEnvironMiddleware', 'RequestLogger',)
