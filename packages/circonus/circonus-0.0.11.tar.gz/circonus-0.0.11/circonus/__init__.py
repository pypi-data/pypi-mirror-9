__title__ = "circonus"
__version__ = "0.0.11"

from logging import NullHandler

import logging

from circonus.client import CirconusClient


logging.getLogger(__name__).addHandler(NullHandler())
