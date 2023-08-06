# -*- mode:python; coding:utf-8; tab-width:4 -*-


class Endpoint:
    def __init__(self, ws_name, host=None, port=None):
        self.ws_name = ws_name
        self.host = host
        self.port = port

    @classmethod
    def from_string(cls, string):
        # string should be "-w <ws> [-h <host>] [-p <port>]"
        # FIXME: use re to parse proxies (or pyparsing)

        fields = [x.strip() for x in string.split()]
        if not '-w' in fields:
            raise ValueError("Invalid proxy format: '{}'".format(string))
        ws = fields[fields.index('-w') + 1]

        host = None
        if '-h' in fields:
            host = fields[fields.index('-h') + 1]

        port = None
        if '-p' in fields:
            port = fields[fields.index('-p') + 1]

        return Endpoint(ws, host, port)

    def __eq__(self, other):
        return (self.ws_name, self.host, self.port) == \
            (other.ws_name, other.ws_name, other.port)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        retval = "-w {}".format(self.ws_name)
        if self.host:
            retval += " -h {}".format(self.host)
        if self.port:
            retval += " -p {}".format(self.port)

        return retval
