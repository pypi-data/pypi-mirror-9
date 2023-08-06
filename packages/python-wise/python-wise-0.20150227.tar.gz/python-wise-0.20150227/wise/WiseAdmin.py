# -*- mode: python; coding: utf-8 -*-

import json
import cPickle as pickle
import os
import time
from commodity.type_ import checked_type

from . import Logging as logging
from .Transceiver import TransceiverFactory
from .Exceptions import ProtocolException
from .endpoint import Endpoint
from .basic_stream import get_typecode
from .frameworks import tornado, django


class ResponseMessage:
    def __init__(self, message, broker):
        self.broker = broker
        data = json.loads(message)

        try:
            self.request_id = data['request_id']
            self.result = self._convert_result(data.get('result', None))
            self.exception = data.get('exception', None)
        except KeyError as e:
            raise ProtocolException(
                "Invalid data format: missing {}, received: '{}'"
                .format(e, data))

    def _convert_result(self, value):
        typecode = get_typecode(value)

        if typecode == "Proxy":
            return self.broker.stringToProxy(value["repr"])

        return value


class TornadoActiveHandler(tornado.WebSocketHandler):
    def initialize(self, broker):
        self.broker = broker
        self._endpoint = None

    def open(self):
        self._endpoint = self.request.uri.strip('/')
        TransceiverFactory.register_handler(self._endpoint, self)

        logging.info("TornadoActiveHandler: new handler for '{}' endpoint"
                     .format(self._endpoint))

    def on_close(self):
        if self._endpoint is not None:
            TransceiverFactory.unregister_handler(self._endpoint)

    def set_response_callback(self, callback):
        self._response_callback = callback

    def on_message(self, message):
        response = ResponseMessage(message, self.broker)
        self._response_callback(response)

    def allow_draft76(self):
        return True


class DjangoActiveHandler(object):
    def __init__(self, broker):
        self.broker = broker
        self._endpoint = None

    def open(self, request):
        self._endpoint = request.path.strip('/')
        TransceiverFactory.register_handler(self._endpoint, self)

        logging.info("DjangoActiveHandler: new handler for '{}' endpoint"
                     .format(self._endpoint))

    def on_close(self):
        if self._endpoint is not None:
            TransceiverFactory.unregister_handler(self._endpoint)

    def set_response_callback(self, callback):
        self._response_callback = callback

    def on_message(self, message):
        response = ResponseMessage(message, self.broker)
        self._response_callback(response)

    def __call__(self, request):
        self.open(request)
        self._ws = request.META["wsgi.websocket"]

        while True:
            try:
                message = self._ws.receive()
                if message is None:
                    break
            except django.WebSocketError:
                break

            self.on_message(message)

        self.on_close()
        del self._ws
        return django.HttpResponse()

    def write_message(self, message):
        self._ws.send(message)


class WiseAdmin:
    "A WebSocket factory for browser Object Adapters"
    def __init__(self, broker):
        self._broker = broker
        self._endpoints = []

        # FIXME: is there something equivalent in the broker class? handlers?
        self._locators = []

        self._db_filename = self._broker.getProperty("Wise.DBFile")
        if self._db_filename is None:
            self._db_filename = "wise.db"

        self._restore_from_db()

    # remote
    def create_socket(self, endpoint, current=None):
        endpoint = Endpoint(endpoint['ws_name'],
                            endpoint.get('host'),
                            endpoint.get('port'))

        self._do_create_socket(endpoint)
        self._save_on_db(endpoint)

    def _restore_from_db(self):
        if not os.path.exists(self._db_filename):
            return

        with file(self._db_filename) as src:
            endpoints = pickle.load(src)
            for ts, e in endpoints:
                self._do_create_socket(e)

    def _save_on_db(self, endpoint):
        now = int(time.time() / 60)  # stored in minutes
        self._endpoints.append((now, checked_type(Endpoint, endpoint)))

        # remove oldest endpoints
        endpoints = []
        for ts, endp in self._endpoints:
            if (now - ts) > 14400:   # 10 days (24*60*10)
                continue
            endpoints.append((ts, endp))

        with file(self._db_filename, "w") as dst:
            pickle.dump(endpoints, dst)

    def _do_create_socket(self, endpoint):
        locator = "^/{}$".format(endpoint.ws_name)
        if locator in self._locators:
            logging.info("WiseAdmin: already registered handler for '{}', "
                         "nothing done".format(locator))
            return

        self._locators.append(locator)
        logging.info("WiseAdmin: create socket for '{}' endpoint".format(
                     endpoint))

        context = dict(broker=self._broker)
        handler = ("^/{}$".format(endpoint.ws_name),
                   self._get_handler(context), context)
        self._broker.registerHandlers([handler])
        logging.info("WiseAdmin: handler registered, {}".format(handler))

    def _get_handler(self, context):
        broker = context['broker']

        if broker.framework == "tornado":
            return TornadoActiveHandler

        if broker.framework == "gunicorn":
            return DjangoActiveHandler(**context)

        raise ValueError("Unknown framework: " + broker.framework)
