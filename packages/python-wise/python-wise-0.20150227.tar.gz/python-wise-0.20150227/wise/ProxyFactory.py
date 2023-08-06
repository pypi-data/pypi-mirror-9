# -*- mode: python; coding: utf-8 -*-

import logging

from .ObjectPrx import ObjectPrx
from .Transceiver import TransceiverFactory
from .endpoint import Endpoint


class ProxyFactory:
    @classmethod
    def create(cls, ic, string):
        assert isinstance(string, (str, unicode))
        (adapter, identity, endpoint) = \
            cls._parse_stringfied_proxy(ic, string)

        # FIXME: make this lazy, get transceiver only when needed.
        #   That would allow the creation of proxies that does not exist (yet).

        # FIXME: raise NoSuchTransceiver instead of None if not transceiver exists
        transceiver = TransceiverFactory.get(endpoint.ws_name)
        if not transceiver:
            logging.warning("Transceiver for endpoint '{}' not available"
                            .format(endpoint.ws_name))
            return None

        return ObjectPrx(identity, endpoint, transceiver)

    @classmethod
    def _parse_stringfied_proxy(cls, ic, string):
        # proxy should be like: "<identity> <endpoint>"
        identity, more = string.split(' ', 1)

        endpoint = Endpoint.from_string(more)
        adapter = ic.resolveAdapter(endpoint = endpoint)

        return adapter, identity, endpoint
