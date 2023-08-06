# -*- mode: python; coding: utf-8 -*-


class BaseException(Exception):
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return str(self.message)


class ProtocolException(BaseException):
    pass


class AlreadyRegisteredException(BaseException):
    pass


class UnknownLocalException(Exception):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        if hasattr(self, 'message'):
            return "{}, {}".format(str(type(self)), self.message)
        return str(type(self))


# Remote exceptions

class OperationNotExistException(Exception):
    pass


class ObjectNotExistException(Exception):
    pass
