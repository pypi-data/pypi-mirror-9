# -*- mode: python; coding: utf-8 -*-

import uuid

from commodity.type_ import checked_type

from .Transceiver import TransceiverApp
from .Exceptions import AlreadyRegisteredException
from .ObjectPrx import ObjectPrx
from .endpoint import Endpoint


class WiseServant(object):
    def __init__(self, servant):
        assert servant is not None
        self._servant = servant

    def __getattr__(self, name):
        return getattr(self._servant, name)

    def wise_getMethodNames(self, current=None):
        # FIXME: refactor with inspect
        return [x for x in dir(self._servant) if not x.startswith("_") and
                callable(getattr(self._servant, x))]


class ObjectAdapter:
    def __init__(self, communicator, name, endpoint):
        self._communicator = communicator
        self._name = name
        self._endpoint = checked_type(Endpoint, endpoint)

        self._asm = {}
        self._properties = {}

        # FIXME: websocket transport specific
        # register transceiver (to handle JSON requests)
        transceiver = TransceiverApp(
            communicator=self._communicator,
            url="^/{}$".format(endpoint.ws_name),
            adapter=self)
        self._communicator.registerApplication(transceiver)

    def getCommunicator(self):
        return self._communicator

    def getName(self):
        return self._name

    def getEndpoint(self):
        return self._endpoint

    def setProperty(self, name, value):
        assert name in ['auth'], "Unknown property: " + name
        self._properties[name] = value

    def getProperty(self, name):
        return self._properties.get(name)

    def add(self, servant, identity):
        if not self._asm.get(identity) is None:
            raise AlreadyRegisteredException("Object: " + identity)
        self._asm[identity] = WiseServant(servant)

        return ObjectPrx(identity, self._endpoint, self)

    def addWithUUID(self, servant):
        identity = str(uuid.uuid1())
        return self.add(servant, identity)

    def find(self, identity):
        return self._asm.get(identity)

    def __repr__(self):
        return ("<wise.ObjectAdapter, name: {}, id: {}>"
                .format(self._name, id(self)))
