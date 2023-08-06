# -*- mode: python; coding: utf-8 -*-

import sys
from threading import Thread, Event
from commodity import path

from . import Logging as logging
from .ObjectAdapter import ObjectAdapter
from .Exceptions import AlreadyRegisteredException
from .StaticFSApplication import StaticFSApplication
from .ProxyFactory import ProxyFactory
from .endpoint import Endpoint
from .frameworks import tornado


PROJECT_DIR = path.find_in_ancestors('project.mk', __file__)
WISE_JS_DIR = path.resolve_path(
    'wise', [
        PROJECT_DIR or "",
        '/usr/share/pyshared',
        '/usr/lib/python2.7/dist-packages',
    ])[0]


# Note: 'tornado' has not support to dynamically adding new handlers
# for existing hosts. This will do it.
class TornadoApplication(tornado.WebApplication):
    def append_handlers(self, host_pattern, host_handlers):
        if not host_pattern.endswith("$"):
            host_pattern += "$"

        specs = None
        for handler in self.handlers:
            if handler[0].pattern == host_pattern:
                specs = handler[1]
                break

        if not specs:
            self.add_handlers(host_pattern, host_handlers)
            return

        for spec in host_handlers:
            if isinstance(spec, tuple):
                assert len(spec) in (2, 3)
                pattern = spec[0]
                handler = spec[1]

                if len(spec) == 3:
                    kwargs = spec[2]
                else:
                    kwargs = {}
                spec = tornado.URLSpec(pattern, handler, kwargs)

            # replace old spec with new one
            assert isinstance(spec, tornado.URLSpec)
            for old in specs[:]:
                if old._path == spec._path:
                    specs.remove(old)
                    break

            specs.append(spec)


class CommunicatorBase(object):
    framework = "unknown"

    def __init__(self, properties):
        if properties is None:
            properties = {}
        assert isinstance(properties, dict)

        self._properties = properties
        self._adapters = {}

    def shutdown(self):
        raise NotImplementedError()

    def waitForShutdown(self):
        raise NotImplementedError()

    def getPropertiesForPrefix(self, prefix, remove_prefix=False):
        retval = {}
        for k, v in self._properties.items():
            if k.startswith(prefix):
                if remove_prefix:
                    k = k[len(prefix):]
                retval[k] = v

        return retval

    def getProperty(self, key):
        return self._properties.get(key, None)

    def getPropertyWithDefault(self, key, default):
        try:
            return self._properties[key]
        except KeyError:
            return default

    def stringToProxy(self, stringfied_proxy):
        return ProxyFactory.create(self, stringfied_proxy)

    def proxyToString(self, proxy):
        return repr(proxy)

    def createObjectAdapter(self, name, endpoint):
        if name in self._adapters:
            raise AlreadyRegisteredException()

        if isinstance(endpoint, (str, unicode)):
            endpoint = Endpoint.from_string(endpoint)

        adapter = ObjectAdapter(self, name, endpoint)
        self._adapters[name] = adapter
        return adapter

    # return adapter name, find by its endpoint
    def resolveAdapter(self, endpoint):
        for name, adapter in self._adapters.items():
            if adapter.getEndpoint() == endpoint:
                return name

    # return adapter name, find by its endpoint
    def resolveEndpoint(self, adapter_name):
        adapter = self._adapters.get(adapter_name, None)
        if not adapter:
            return None
        return adapter.getEndpoint()

    def registerApplication(self, application):
        self.registerHandlers(application.get_handler_spec())

    def registerHandlers(self, handlers, host):
        raise NotImplementedError

    def get_url(self, location):
        raise NotImplementedError


class TornadoCommunicator(Thread, CommunicatorBase):
    framework = "tornado"

    def __init__(self, host, port, properties=None):
        Thread.__init__(self)
        CommunicatorBase.__init__(self, properties)

        if self._properties.get("TornadoApp.debug", False):
            logging.warning("Wise: Debug Mode enabled, remove on production!!")

        self.port = port
        self.host = host
        self.url = "http://{}:{}".format(self.host, self.port)

        self.is_ready = Event()
        self.daemon = True
        self.start()

    def run(self):
        prefix = "TornadoApp."
        properties = self.getPropertiesForPrefix(prefix, True)
        self._tornado = TornadoApplication(**properties)

        # NOTE: no_keep_alive is True, because otherwise, if the
        # handler is changed (or the communicator is destroyed and
        # created again), an old client will be served using the old
        # handler (binded on HTTPConnection)

        self._http_server = tornado.HTTPServer(
            self._tornado, no_keep_alive=True)
        logging.info("Communicator: http server on {}:{}".format(self.host, self.port))
        self._http_server.listen(self.port, self.host)

        self._register_static_files_handler()
        self.is_ready.set()
        tornado.IOLoop.instance().start()

    def shutdown(self):
        if not hasattr(self, "_http_server"):
            return

        self._http_server.stop()
        tornado.IOLoop.instance().stop()

    # handlers is a list of (url, class, params)
    def registerHandlers(self, handlers, host=".*$"):
        self._tornado.append_handlers(host, handlers)

    def waitForShutdown(self):
        try:
            while True:
                self.join(1000)
                if not self.isAlive():
                    break
        except KeyboardInterrupt:
            pass

    def _register_static_files_handler(self):
        # register static files handler (to serve wise.js and others)
        static_files = StaticFSApplication(
            communicator=self, locator='/wise/', path=WISE_JS_DIR)
        self.registerApplication(static_files)

    def get_url(self, location):
        "returns a uri within the server"
        return "http://{}:{}/{}".format(self.host, self.port, location)

    def register_StaticFS(self, locator, path, index=''):
        frontend = StaticFSApplication(self, locator, path, index)
        self.registerApplication(frontend)
        return frontend

    def registerRedirect(self, from_, to_):
        class RedirectHandler(tornado.RequestHandler):
            def get(self):
                self.redirect(to_)

        self.registerHandlers([(from_, RedirectHandler, [])])


class GunicornCommunicator(CommunicatorBase):
    framework = "gunicorn"

    def registerHandlers(self, handlers, host=""):

        # Note: import here, only when needed
        from django.conf import settings
        from django.conf.urls import patterns, url
        from django.utils.importlib import import_module

        urls = sys.modules.get(settings.ROOT_URLCONF)
        if urls is None:
            urls = import_module(settings.ROOT_URLCONF)

        for pattern, handler, context in handlers:
            if pattern.startswith("^/"):
                pattern = '^' + pattern[2:]
            urls.urlpatterns += patterns(host, url(pattern, handler))


# Default backend server is "tornado"
Communicator = TornadoCommunicator
