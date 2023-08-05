"""Request hooks related to uniquely identifying requests."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import uuid

from ... import context


LOG = logging.getLogger(__name__)


def unique_request(request):
    """Assign a UUID to the request.

    This hook will first look in the environ for a UUID. If found, it will
    assign that UUID to the request object. If not found it will create a
    new UUID for the request. It will also ensure that the request_id attribute
    of the context storage is set.

    This hook will search the headers for a 'Request-Id' header which contains
    the UUID of the request. This makes it possible to pass unique id's across
    requests for tracking purposes.

    This hook can work in with the UniqueEnvironMiddleware or on its own. It
    adds a 'uuid' attribute to the request for easy access during a request.
    """
    request.uuid = request.environ.setdefault(
        'HTTP_REQUEST_ID',
        str(uuid.uuid4()),
    )
    LOG.debug('Modified request object with uuid %s.', request.uuid)
    if not hasattr(context.storage, 'request_id'):

        context.storage = request.uuid


__all__ = ('unique_request',)
