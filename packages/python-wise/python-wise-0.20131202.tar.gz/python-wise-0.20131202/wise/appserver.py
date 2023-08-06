# -*- mode: python; coding: utf-8 -*-

import os
import importlib
import logging
from tornado import web, template

from .utils import initialize
from .StaticFSApplication import StaticFSApplication
from .WebApplication import WebApplication

import settings

logger = logging.getLogger("Wise")
logger.setLevel(logging.DEBUG)

pwd = os.path.abspath(os.path.dirname(settings.__file__))


class MultiPathLoader(template.BaseLoader):
    def __init__(self, directories, **kwargs):
        template.BaseLoader.__init__(self, **kwargs)

        self.paths = []
        for d in directories:
            self.paths.append(os.path.abspath(d))

    def resolve_path(self, name, parent_path=None):
        for root in self.paths:
            template_path = os.path.join(root, name)
            if os.path.exists(template_path):
                return template_path

        return name

    def _create_template(self, path):
        logger.debug("creating template from {}".format(path))
        name = os.path.split(path)[1]
        with file(path, "rb") as src:
            return template.Template(src.read(), name=name, loader=self)


# dirty hack to get control over errors in tornado
class ErrorHandler(web.RequestHandler):
    def initialize(self, status_code):
        self.set_status(status_code)

    def get_template_path(self):
        return os.path.join(pwd, "templates/")

    def prepare(self):
        if not hasattr(self, "status_code"):
            return

        if self.status_code == 404:
            return self.render("error404.html")

        raise web.HTTPError(self.status_code)

web.ErrorHandler = ErrorHandler


class AppServer(object):
    def __init__(self, name, host="127.0.0.1", port=8080, debug=False):
        self.name = name
        self.host = host
        self.port = port

        if debug:
            logger.info("###### DEBUG MODE ENABLED, REMOVE ON PRODUCTION!!")

        props = {"TornadoApp.debug": debug, "WiseSaver.dbfiles": 'wisedb.cache'}
        self.ws = initialize(host, port, props)
        self.wise_adapter = self.ws.createObjectAdapter("Adapter", "-w server")

        self.register_apps()

    def register_apps(self):
        for app_name in settings.INSTALLED_APPS:
            if not self.app_is_healthy(app_name):
                logger.warning("could not load '{}' app".format(app_name))
                continue

            self.initialize_app(app_name)
            self.register_static_handler_for_app(app_name)
            self.register_views_for_app(app_name)
            self.register_servants_for_app(app_name)

        self.register_common_static_handler()
        self.register_common_urls()
        self.register_common_servants()

    def app_is_healthy(self, app_name):
        try:
            urls = importlib.import_module("{}.urls".format(app_name), self.name)
        except ImportError as e:
            logger.warning(str(e))
            logger.warning("could not load urls from module '{}'".format(app_name))
            return False

        if not hasattr(urls, "urlpatterns"):
            logger.warning("app '{}' has not urlpatterns in urls module".format(app_name))
            return False

        return True

    def initialize_app(self, name):
        module = importlib.import_module("{}".format(name), self.name)
        if hasattr(module, "init_app"):
            module.init_app(self.broker, self.wise_adapter)

    def register_static_handler_for_app(self, name):
        path = os.path.join(pwd, name + "/static")
        if not os.path.exists(path):
            return

        class StaticFileHandlerApp(WebApplication):
            def get_handler_class(self):
                return web.StaticFileHandler

            def get_handler_params(self):
                return {"path": path}

        url = "^/{}/static/(.*)".format(name)
        app = StaticFileHandlerApp(self.ws, url)
        self.ws.registerApplication(app)

    def register_views_for_app(self, name):
        common_templates_path = os.path.join(pwd, "templates/")

        urls = importlib.import_module("{}.urls".format(name), self.name)
        for locator, handler_ in urls.urlpatterns.items():
            url = "^/{}/{}".format(name, locator)

            class RequestHandler(web.RequestHandler):
                handler = handler_

                def get(self):
                    context = {
                        'APP_STATIC_PATH': "/{}/static".format(name)
                    }
                    return self.handler(context)

                def create_template_loader(self, path):
                    app_template_path = os.path.join(path, "templates")

                    all_paths = []
                    if os.path.exists(app_template_path):
                        all_paths.append(app_template_path)

                    all_paths.append(common_templates_path)
                    return MultiPathLoader(all_paths)

            class RequestHandlerApp(WebApplication):
                def get_handler_class(self):
                    RequestHandler.url = url
                    return RequestHandler

            app = RequestHandlerApp(self.ws, url)
            self.ws.registerApplication(app)

    def register_servants_for_app(self, name):
        try:
            servants = importlib.import_module("{}.servants".format(name), self.name)
            servants.register_servants(self.wise_adapter)
        except Exception as e:
            logger.warning(str(e))
            logger.warning("could not load servants from module '{}'".format(name))
            return

    def register_common_static_handler(self):
        path = os.path.join(pwd, "static/")
        static_app = StaticFSApplication(self.ws, '/static/', path)
        self.ws.registerApplication(static_app)

    def register_common_urls(self):
        common_templates_path = os.path.join(pwd, "templates/")

        try:
            urls = importlib.import_module("urls", self.name)
        except ImportError:
            return

        for locator, handler_ in urls.urlpatterns.items():
            url = "^/{}".format(locator)

            class RequestHandler(web.RequestHandler):
                handler = handler_

                def get(self):
                    return self.handler({})

                def create_template_loader(self, path):
                    all_paths = [common_templates_path]
                    return MultiPathLoader(all_paths)

            class RequestHandlerApp(WebApplication):
                def get_handler_class(self):
                    return RequestHandler

            app = RequestHandlerApp(self.ws, url)
            self.ws.registerApplication(app)

    def register_common_servants(self):
        try:
            servants = importlib.import_module("servants")
            servants.register_servants(self.wise_adapter)
        except Exception as e:
            logger.info(str(e))
            logger.info("could not load common servants")
            return

    def communicator(self):
        return self.ws

    def run(self):
        self.ws.waitForShutdown()

    def stop(self):
        self.ws.shutdown()

