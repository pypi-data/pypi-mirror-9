# -*- mode: python; coding: utf-8 -*-

import traceback
import jsonpickle
from threading import Event, Lock
from commodity.thread_ import SimpleThreadPool
from commodity.os_ import FuncAsFile

from . import Logging as logging
from .WebApplication import WebApplication
from .Exceptions import (ProtocolException, UnknownLocalException,
                         OperationNotExistException, ObjectNotExistException)
from .Current import Current
from .basic_stream import get_typecode, any_to_marshable, exception_to_marshable
from .frameworks import tornado, django


class TransceiverApp(WebApplication):
    def __init__(self, communicator, url, adapter):
        WebApplication.__init__(self, communicator, url)
        self._adapter = adapter
        self._framework = communicator.framework

        if self._framework != "gunicorn":
            self._thread_pool = SimpleThreadPool(1)

    def get_handler_class(self):
        if self._framework == "tornado":
            return TornadoMessageHandler

        if self._framework == "gunicorn":
            return DjangoMessageHandlerFactory(**self.get_handler_params())

        raise ValueError("Unknown Communicator framework: " + self._framework)

    def get_handler_params(self):
        retval = {'adapter': self._adapter}
        if self._framework == "tornado":
            retval['thread_pool'] = self._thread_pool

        return retval


class Transceiver:
    def __init__(self, handler):
        self._handler = handler
        self._handler.set_response_callback(self.on_response)
        self._request_id = 0
        self._request_id_lock = Lock()
        self._pending_responses = {}

    def send_request(self, request):
        with self._request_id_lock:
            request_id = self._request_id
            self._request_id += 1

        request['request_id'] = request_id
        request = jsonpickle.encode(request)

        # FIXME: this depends on oneway|twoway invocation
        barrier = Event()
        self._pending_responses[request_id] = [barrier, None]
        self.send(request)
        ok = barrier.wait(5)
        response = self._pending_responses.pop(request_id)[1]

        if not ok:
            raise RuntimeError("Remote object did not response in time!")

        self.raise_exception_if_any(response.exception)
        return response.result

    @staticmethod
    def raise_exception_if_any(e):
        if not e:
            return

        if e['name'] == "ObjectNotExistException":
            raise ObjectNotExistException(e['message'])

        if e['name'] == "OperationNotExistException":
            raise OperationNotExistException(e['message'])

        raise UnknownLocalException(**e)

    # FIXME: only called for twoway invocations
    def on_response(self, response):
        self._pending_responses[response.request_id][1] = response
        barrier = self._pending_responses[response.request_id][0]
        barrier.set()

    def send(self, request):
        if self._handler is None:
            raise RuntimeError("Can not reach remote object!")

        try:
            self._handler.write_message(request)
        except Exception as e:
            self._handler = None
            raise RuntimeError("Error sending message to remote object: {}".format(e))


class TransceiverFactory:
    _handlers = {}
    _transceivers = {}

    @classmethod
    def register_handler(cls, wslocator, handler):
        logging.info("TransceiverFactory: register handler for '{}'".format(wslocator))
        cls._handlers[wslocator] = handler

    @classmethod
    def unregister_handler(cls, wslocator):
        logging.info("TransceiverFactory: un-register handler for '{}'".format(wslocator))
        cls._handlers.pop(wslocator, None)
        cls._transceivers.pop(wslocator, None)

    @classmethod
    def get(cls, wslocator):
        logging.info("TransceiverFactory: get for websocket '{}'".format(wslocator))

        # FIXME is the default value for get() (many times)
        transceiver = cls._transceivers.get(wslocator, None)
        if transceiver:
            return transceiver

        handler = cls._handlers.get(wslocator, None)
        if not handler:
            logging.error("TransceiverFactory: ERROR: no handler for websocket '{}'"
                          .format(wslocator))

            return None

        logging.info("TransceiverFactory: creating new for websocket '{}'"
                     .format(wslocator))
        transceiver = Transceiver(handler)
        cls._transceivers[wslocator] = transceiver
        return transceiver


class RequestMessage:
    def __init__(self, message, communicator):
        self.communicator = communicator

        # FIXME: JSON encoding process specific
        # perhaps something like:
        # data = communicator.encoding.decode(message)
        data = jsonpickle.decode(message)

        try:
            self.request_id = data['request_id']
            self.identity = data['identity']
            self.method = data['method']
            self.params = self._convert_params(data)

        except KeyError as e:
            raise ProtocolException(
                "Invalid message format: missing {}, received: '{}'"
                .format(e, message))

    # FIXME: mixed JSON unmarshalling process and typecoding
    def _convert_params(self, data):
        if not 'params' in data:
            return {}

        params = data['params']
        if not isinstance(params, list):
            raise ValueError("Invalid params: '{}'".format(params))

        for i, param in enumerate(params):
            typecode = get_typecode(param)

            if typecode == "Proxy":
                params[i] = self.communicator.stringToProxy(param["repr"])

        return params

    def __str__(self):
        return ("request_id: {.request_id}\n"
                "identity: {.identity}\n"
                "method: {.method}\n"
                "params: {.params}\n"
                .format(self))


class BaseMessageHandler(object):
    def _handle_on_message(self, message, http_request=None):
        try:
            request = RequestMessage(message, self._adapter._communicator)
            method = self._get_object_method(request)
            if not method:
                return

            current = Current(self, self._adapter, request=http_request)
            try:
                retval = method(*request.params + [current])
            except TypeError as e:
                fd = FuncAsFile(logging.info, "exc:| ")
                traceback.print_exc(None, fd)

                logging.error("Invalid Params: '{}'".format(request.params))
                raise

            self._response(request.request_id, retval)

        except ProtocolException as e:
            logging.warning(str(e))
            self._raise_remote_exception(-1, e)

        except Exception as e:
            fd = FuncAsFile(logging.info, "exc:| ")
            traceback.print_exc(None, fd)

            message = ("Error while calling method '{}.{}': '{}'".
                       format(request.identity, request.method, e))
            logging.warning(message)
            self._raise_remote_exception(request.request_id, e)

    def _response(self, request_id, result):
        response = dict(request_id=request_id,
                        result=any_to_marshable(result))

        self.write_message(jsonpickle.encode(response))

    def _get_object_method(self, request):
        obj = self._find_servant(request)
        if not obj:
            return

        method = getattr(obj, request.method, None)
        if not method:
            self._raise_remote_exception(
                request.request_id,
                OperationNotExistException(request.method))
        return method

    def _find_servant(self, request):
        servant = self._adapter.find(request.identity)
        if not servant:
            self._raise_remote_exception(
                request.request_id,
                ObjectNotExistException(request.identity))
        return servant

    def _raise_remote_exception(self, request_id, exc):
        response = dict(request_id=request_id,
                        error=exception_to_marshable(exc))

        self.write_message(jsonpickle.encode(response))


class TornadoMessageHandler(tornado.WebSocketHandler, BaseMessageHandler):
    async = True

    def initialize(self, adapter, thread_pool):
        self._adapter = adapter
        self._is_closed = False
        self._thread_pool = thread_pool

    def open(self):
        endpoint = self._adapter.getEndpoint()
        TransceiverFactory.register_handler(endpoint, self)

    def on_close(self):
        endpoint = self._adapter.getEndpoint()
        TransceiverFactory.unregister_handler(endpoint)
        self._is_closed = True

    @property
    def is_closed(self):
        return self._is_closed

    def on_message(self, message):
        if self.async:
            logging.info("MessageHandler: async dispatching for {}".format(repr(message)))
            self._thread_pool.add(self._handle_on_message, (message,))
        else:
            self._handle_on_message(message)

    def allow_draft76(self):
        return True


class DjangoMessageHandlerFactory(object):
    def __init__(self, adapter):
        self._adapter = adapter

    def __call__(self, request):
        return DjangoMessageHandler(self._adapter)(request)


class DjangoMessageHandler(BaseMessageHandler):
    def __init__(self, adapter):
        self._adapter = adapter

    def __call__(self, request):
        self._ws = request.META["wsgi.websocket"]

        self._update_request(request)
        while True:
            try:
                message = self._ws.receive()
                if message is None:
                    break
            except django.WebSocketError:
                break

            try:
                self._handle_on_message(message, request)
            except:
                del self._ws
                raise

        del self._ws
        return django.HttpResponse()

    def _update_request(self, request):
        session = None
        user = None

        sessionid = request.COOKIES.get('sessionid')
        if sessionid:

            # FIXME: coupled with mongoDB!
            # late import of this, to let django init settings
            from mongoengine.django.sessions import MongoSession
            from mongoengine.django.auth import User

            try:
                session = MongoSession.objects.get(session_key=sessionid)
                uid = session.get_decoded().get('_auth_user_id')
                if uid:
                    user = User.objects.get(pk=uid)
            except MongoSession.DoesNotExist:
                pass

        request.user = user
        request.session = session

    def write_message(self, message):
        self._ws.send(message)
