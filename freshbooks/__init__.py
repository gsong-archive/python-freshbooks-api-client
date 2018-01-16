import logging

from .__version__ import __version__
from .api import Client

__title__ = 'python-freshbooks-api-client'
__author__ = 'George Song'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 George Song'


# Set default logging handler to avoid "No handler found" warnings.
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger(__name__).addHandler(NullHandler())
