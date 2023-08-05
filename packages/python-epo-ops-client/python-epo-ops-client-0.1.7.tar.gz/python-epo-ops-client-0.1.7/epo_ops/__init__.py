# -*- coding: utf-8 -*-

import logging

from .__version__ import __version__
from .api import Client, RegisteredClient

__title__ = 'python-epo-ops-client'
__ops_version__ = '3.1'
__author__ = 'George Song'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2014 55 Minutes'


# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:  # pragma: no cover
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
