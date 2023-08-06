# -*- mode: python; coding: utf-8 -*-


class Current:
    def __init__(self, ws_handler, adapter, **kwargs):
        self.ws_handler = ws_handler
        self.adapter = adapter
        self.context = kwargs
