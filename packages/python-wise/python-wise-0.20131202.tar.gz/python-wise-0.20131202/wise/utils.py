# -*- mode: python: coding: utf-8 -*-

import os
import socket

from .Communicator import TornadoCommunicator, GunicornCommunicator
from .WiseAdmin import WiseAdmin
from . import Logging as logging


__ic = None


def initialize(host=None, port=None, properties=None, server="tornado"):
    assert __ic is None, "Only one communicator instance is supported"

    properties = properties or {}

    if server == "tornado":
        host = host or "127.0.0.1"
        port = port if port is not None else "8080"
        return _initialize_for_tornado(host, port, properties)

    if server == "gunicorn":
        if host is not None or port is not None:
            logging.info("Wise: Using gunicorn, ignoring host and port properties")
        return _initialize_for_gunicorn(properties)

    raise ValueError("Unknown backend server:", + server)


def _initialize_for_tornado(host, port, properties):
    global __ic

    host = host or socket.gethostbyname_ex(socket.gethostname())[0]
    __ic = TornadoCommunicator(host=host, port=port, properties=properties)
    __ic.is_ready.wait()

    admin_adapter = __ic.createObjectAdapter("WiseAdmin", "-w wise")
    admin_adapter.add(WiseAdmin(__ic), "WiseAdmin")

    return __ic


def _initialize_for_gunicorn(properties):
    global __ic

    __ic = GunicornCommunicator(properties=properties)

    admin_adapter = __ic.createObjectAdapter("WiseAdmin", "-w wise")
    admin_adapter.add(WiseAdmin(__ic), "WiseAdmin")

    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            module = __import__(app + ".servants")
            module.servants.initialize(__ic)
        except ImportError as e:
            if not str(e).endswith("servants"):
                logging.error("loader: unable to load '{}', {}".format(app, str(e)))

    return __ic


def dirname(path):
    return os.path.abspath(os.path.dirname(path))


class Application(object):
    def __init__(self):
        self.broker = initialize()

    def main(self, argv=None):
        self.run(argv or [])


def add_placeholder(method):
    def deco(*args):
        return method(*args[:-1])
    return deco


class proxy_as_servant(object):
    def __init__(self, proxy):
        for name in proxy.wise_getMethodNames():
            setattr(self, name, add_placeholder(getattr(proxy, name)))
