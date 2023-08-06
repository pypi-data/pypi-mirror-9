# -*- mode: python; coding: utf-8 -*-


class WebApplication:
    def __init__(self, communicator, url):
        self._communicator = communicator
        self._url = url

    def get_handler_url(self):
        return self._url

    def get_formatted_url(self):
        raise NotImplementedError

    def get_handler_class(self):
        raise NotImplementedError

    def get_handler_params(self):
        return {}

    def get_handler_spec(self):
        return [(self.get_handler_url(),
                self.get_handler_class(),
                self.get_handler_params())]

    def get_url(self):
        return self._communicator.url + self.get_formatted_url()
