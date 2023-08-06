# -*- mode: python; coding: utf-8 -*-

import os
import logging

from .WebApplication import WebApplication
from .frameworks import tornado


class StaticFSApplication(WebApplication):
    def __init__(self, communicator, locator, path, index=""):
        if locator == "/":
            logging.warning("Do not register applications on '/', "
                            "it will interfere with websocket handlers")

        if not locator.endswith("/"):
            locator += "/"

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.isdir(path):
            path = os.path.dirname(path)

        self._locator = locator
        self._path = path
        self._index = index

        WebApplication.__init__(self, communicator=communicator, url=path)
        logging.debug("Serving static content '{}' as '{}'".format(path, locator))

    def get_handler_url(self):
        return r"{}(.*)".format(self._locator)

    def get_formatted_url(self):
        return self._locator + self._index

    def get_handler_class(self):
        return tornado.StaticFileHandler

    def get_handler_params(self):
        return {'path': self._path}
