"""Thread-local, global request contexts.

Attributes:
    storage (werkzeug.local.Local): A thread-local storage object which can be
        used to store data related to a request.

Note:
    The thread-local storage works by partitioning data on the thread id. Each
    context should be torn down at the end of a request/thread to avoid stale
    data appearing in subsequent threads with the same thread id. This can
    be accomplished by using the werkzeug.local.release_local on the storage
    object in this module. There is a middleware bundled with this package
    which automates this process.
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug import local


storage = local.Local()


def clear():
    """Clear the local storage container."""
    local.release_local(storage)

__all__ = ('storage', 'clear')
