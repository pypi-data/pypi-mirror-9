# -*- mode: python; coding: utf-8 -*-

from threading import Lock
from commodity.thread_ import WorkerGroup

from . import Logging as logging


class Observable:
    def __init__(self):
        self.observers = []
        self.observers_lock = Lock()

        self.group = WorkerGroup(10)

    def attach(self, observer, current):
        ws = current.adapter.getCommunicator()
        observer = ws.stringToProxy(observer)

        if observer is None or observer in self.observers:
            return

        logging.info("{}: attach view, '{}'".format(self.__class__.__name__, observer))
        self.observers.append(observer)

    def detach(self, observer, current):
        ws = current.adapter.getCommunicator()
        observer = ws.stringToProxy(observer)

        self._do_detach(observer)

    def _do_detach(self, observer):
        with self.observers_lock:
            if not observer in self.observers:
                return False

            self.observers.remove(observer)
        logging.info("{}: detach view, '{}'".format(self.__class__.__name__, observer))
        return True

    def notify(self, method_name, *args):
        if not method_name:
            method_name = "notify"

        for observer in self.observers[:]:
            worker = self.group.get_worker(observer.endpoint.ws_name)
            worker.add(self._notify_observer, (observer, method_name,) + args)

    def _notify_observer(self, observer, method_name, *args):
        try:
            method = getattr(observer, method_name)
            method(*args)
        except Exception as e:
            if self._do_detach(observer):
                logging.warning(
                    "Exception raised when reaching observer: {}\n"
                    "Removing observer '{}'".format(e, observer))


class PersistentObservable(Observable):
    def __init__(self, db, namespace):
        # db es un objeto que encapsula el acceso a la persistencia
        # namespace es un dominio a usar cada vez que se accede a db
        # db.get_observers(namespace)
        # db.add_observer(namespace, observer)
        pass
