"""Application implementations which leverage werkzeug Map and Rule objects."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from itertools import chain

from werkzeug.routing import Map

from . import base


class MapApplication(base.BaseApplication):

    """Application which uses werkzeug Maps for routing."""

    def __init__(self, routes, before=(), after=(), request=None):
        """Initialize the application with a Map router.

        Args:
            routes (Map): A werkzeug routing Map. Each endpoint
                registered with the Map must implement the Endpoint interface.
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
        super(MapApplication, self).__init__(before, after, request=request)
        self._url_map = routes

    def route(self, request):
        """Determine the endpoint of the request.

        Args:
            request (BaseRequest): The request object to route.

        Returns:
            tuple: A tuple containing the routing endpoint and any keyword
                arguments which should be passed to the endpoint upon
                execution.
        """
        urls = self._url_map.bind_to_environ(request.environ)
        endpoint, kwargs = urls.match()
        return endpoint(), kwargs


class MapPluginApplication(MapApplication):

    """Application which builds a router Map using a series of plugins."""

    def __init__(self, plugins=(), before=(), after=(), request=None):
        """Initialize the application with a series of plugins.

        Args:
            plugins (iter of plugins): An iterable of objects which have a
                'urls' and optional 'converters' properties. The 'urls'
                property must be an iterable of werkzeug Rule objects. The
                'converters' property, if given, must be a mapping of names to
                converter objects. The plugin properties maybe exposed as
                object attributes or mapping keys.
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
        # Build a list of url endpoints from the service interfaces.
        app_urls = ()
        converters = {}
        for plugin in plugins:

            app_urls = chain(
                app_urls,
                (
                    plugin.urls
                    if hasattr(plugin, 'urls')
                    else plugin['urls']
                )
            )

            # Check for custom converters used by an application.
            custom_converters = {}
            if hasattr(plugin, 'converters'):

                custom_converters = plugin.converters

            elif isinstance(plugin, dict) and 'converters' in plugin:

                custom_converters = plugin['converters']

            converters = dict(
                chain(converters.items(), custom_converters.items()),
            )

        super(MapPluginApplication, self).__init__(
            Map(tuple(app_urls), converters=converters),
            before,
            after,
            request=request,
        )


__all__ = ('MapApplication', 'MapPluginApplication',)
