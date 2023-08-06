# -*- mode: python; coding: utf-8 -*-

# Imports not used here, made available for the wise users
from .Communicator import Communicator
from .WiseAdmin import WiseAdmin
from .WebApplication import WebApplication
from .StaticFSApplication import StaticFSApplication
from .Object import Observable

try:
    from .appserver import AppServer
except ImportError as e:
    print "[wise] Error: AppServer not available:", e

from .utils import initialize, dirname, Application, proxy_as_servant

