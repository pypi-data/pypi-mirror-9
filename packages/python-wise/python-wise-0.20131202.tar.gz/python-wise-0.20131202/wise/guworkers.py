# -*- mode: python; coding: utf-8 -*-

from geventwebsocket.handler import WebSocketHandler
from gunicorn.workers.ggevent import GeventPyWSGIWorker

from utils import initialize


class GeventWebSocketWorker(GeventPyWSGIWorker):
    wsgi_handler = WebSocketHandler
    broker = initialize(server="gunicorn")

