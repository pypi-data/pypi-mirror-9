# -*- mode: python; coding: utf-8 -*-

from . import Logging as logging


class EmptyClass(object):
    def __init__(self, *args, **kwargs):
        pass


class tornado(object):
    pass


try:
    from tornado.websocket import WebSocketHandler
    tornado.WebSocketHandler = WebSocketHandler

    from tornado.web import StaticFileHandler, Application, URLSpec, RequestHandler
    tornado.StaticFileHandler = StaticFileHandler
    tornado.WebApplication = Application
    tornado.URLSpec = URLSpec
    tornado.RequestHandler = RequestHandler

    from tornado.httpserver import HTTPServer
    tornado.HTTPServer = HTTPServer

    from tornado.ioloop import IOLoop
    tornado.IOLoop = IOLoop

except ImportError:
    logging.info("Tornado: framework not available")

    tornado._not_available_ = True
    tornado.WebSocketHandler = EmptyClass
    tornado.StaticFileHandler = EmptyClass
    tornado.WebApplication = EmptyClass
    tornado.URLSpec = EmptyClass
    tornado.RequestHandler = EmptyClass
    tornado.HTTPServer = EmptyClass
    tornado.IOLoop = EmptyClass


class django(object):
    pass


try:
    from geventwebsocket.exceptions import WebSocketError
    django.WebSocketError = WebSocketError

    from django.http import HttpResponse, HttpResponseForbidden
    django.HttpResponse = HttpResponse
    django.HttpResponseForbidden = HttpResponseForbidden

except ImportError:
    logging.info("Django: framework not available")

    django._not_available_ = True
    django.WebSocketError = EmptyClass
    django.HttpResponse = EmptyClass
    django.HttpResponseForbidden = EmptyClass


assert \
    not hasattr(django, "_not_available_") or \
    not hasattr(tornado, "_not_available_"), \
    "Wise needs a framework to run, install either tornado or django"


