# -*- mode: python; coding: utf-8 -*-

from commodity.type_ import checked_type

from endpoint import Endpoint
from basic_stream import any_to_marshable


class MethodHandler(object):
    def __init__(self, identity, transceiver, method_name):
        self._identity = identity
        self._transceiver = transceiver
        self._method_name = method_name

    def __call__(self, *args):
        return self._transceiver.send_request(
            {'identity': self._identity,
             'method': self._method_name,
             'params': any_to_marshable(args)})


class ObjectPrx(object):
    def __init__(self, identity, endpoint, transceiver):
        self.identity = identity
        self.endpoint = checked_type(Endpoint, endpoint)
        self._transceiver = transceiver

    def wise_getIdentity(self):
        return self.identity

    def to_marshable(self):
        return dict(wise_typecode="Proxy", repr=repr(self))

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        return MethodHandler(self.identity, self._transceiver, name)

    def __nonzero__(self):
        return self.identity is not None and self._transceiver is not None

    def __eq__(self, other):
        return isinstance(other, ObjectPrx) and \
            (self.identity, self.endpoint) == (other.identity, other.endpoint)

    def __repr__(self):
        return "{} {}".format(self.identity, self.endpoint)

    def __str__(self):
        return repr(self)
