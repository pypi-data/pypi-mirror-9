======
RESTpy
======

**Werkzeug utilities for building RESTful services.**

What is RESTpy?
===============

RESTpy is a small set of utilities built on Werkzeug that make it a little
easier to roll out a RESTful web service. This project defines very few unique
features outside of Werkzeug itself. Think of it like flask but with even
*less* features.

Simple Usage Example
====================

.. code-block:: python

    from restpy.api import Application
    from restpy.api import Endpoint

    from werkzeug.routing import Map
    from werkzeug.routing import Rule
    from werkzeug.wrappers import Response


    # Endpoints define HTTP verb methods to handle requests.
    class IndexEndpoint(Endpoint):

        def get(self, request):
            return Response("get")

        def post(self, request):
            return Response("post")

        def put(self, request):
            return Response("put")

        def delete(self, request):
            return Response("delete")

    # URL mappings are normal Werkzeug routing Maps.
    urls = Map([
        Rule("/", endpoint=IndexEndpoint)
    ])

    # This object can be exposed to any WSGI server.
    application = Application(urls)

Request/Response Hooks
======================

RESTpy, in addition to supporting any standard WSGI middleware, supports the
registration of global request and response hooks. Request hooks are any Python
callable which accepts the current request as a first argument. Response hooks,
likewise, accept the request and response as arguments. These can be used to
inject generic functionality, like authentication, without writing your own
middlewares.

.. code-block:: python

    import logging
    from werkzueg.exceptions import Unauthorized

    LOG = logging.getLogger(__name__)


    def authenticate(request):
        """A hook which checks for the secret key."""
        if request.headers.get('Secrete-Token', None) != 42:

            raise Unauthorized()


    def log_complete(request, response):
        """Log a message after every request."""
        LOG.debug('Request complete!')

    application = Application(
        urls,
        before=(authenticate,),
        after=(log_complete,)
    )

The 'before' and 'after' keyword arguments will accept any iterable of hooks.
These hooks will be executed on each request.

Thread-Local Storage
====================

Sharing data between middlewares, hooks, and endpoints can be difficult in
multi-threaded, or green-threaded, environments. To assist, this package makes
it easy to use the Werkzueg local objects to share data globally within a
thread.

.. code-block:: python

    import uuid

    from restpy.api import Application
    from restpy.api import ContextClearMiddleware
    from restpy.api import Endpoint
    from restpy import context

    from werkzeug.routing import Map
    from werkzeug.routing import Rule
    from werkzeug.wrappers import Response

    class ThreadedEndpoint(Endpoint):

        def get(self, request):
            return Response(context.storage.unique_value)

    def unique_value(request):
        """Set a random to the context storage."""
        context.storage.unique_value = (uuid.uuid4())

    urls = Map([
        Rule("/", endpoint=ThreadedEndpoint)
    ])

    # Set the thread context to clear after each request.
    application = ContextClearMiddleware(
        Application(urls, before=(unique_value,))
    )

The above example will generate a unique value for each request and return it
in a GET request. If the WSGI application is run in a multi-threaded
environment, using eventlet or gevent for example, the value will be unique to
the thread which is executing. The ContextClearMiddleware helps ensure that
stale data doesn't stick around after a thread is complete.

Unique Request ID's
===================

Bundled with this project are a middleware and request hook which work together
to provide a UUID for each request that hits an application. These helpers make
use of the context storage to allow for easy logging of the request id as well.

.. code-block:: python

    import logging

    from restpy.api import Application
    from restpy.api import ContextClearMiddleware
    from restpy.api import Endpoint
    from restpy.api import RequestLogger
    from restpy.api import unique_request
    from restpy.api import UniqueEnvironMiddleware

    from werkzeug.routing import Map
    from werkzeug.routing import Rule
    from werkzeug.wrappers import Response

    class UniqueEndpoint(Endpoint):

        def get(self, request):
            return Response(request.uuid)

    urls = Map([
        Rule("/", endpoint=UniqueEndpoint)
    ])

    # Set the thread context to clear after each request.
    application = ContextClearMiddleware(
        UniqueEnvironMiddleware(
            Application(urls, before=(unique_request))
        )
    )

    logging.basicConfig(
        format='%(levelname)s:%(request_id)s:%(message)s',
        level=logging.DEBUG,
    )
    logging.setLoggerClass(RequestLogger)

The above example configures the application to generate a new UUID for every
request, store this uuid on the request object and context storage, and
configure logging to include the unique request id in every log message.

License
=======

This project is released under the same BSD license as Werkzeug::

    Copyright (c) 2013 by Kevin Conway

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.

        * Redistributions in binary form must reproduce the above
          copyright notice, this list of conditions and the following
          disclaimer in the documentation and/or other materials provided
          with the distribution.

        * The names of the contributors may not be used to endorse or
          promote products derived from this software without specific
          prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Contributor's Agreement
=======================

All contributions to this project are protected by the contributors agreement
detailed in the CONTRIBUTING file. All contributors should read the file before
contributing, but as a summary::

    You give us the rights to distribute your code and we promise to maintain
    an open source release of anything you contribute.
