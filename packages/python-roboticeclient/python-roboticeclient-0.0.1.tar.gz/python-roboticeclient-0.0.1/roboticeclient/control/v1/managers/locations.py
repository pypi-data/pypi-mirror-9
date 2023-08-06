
"""
Manager for devices
"""

import sys
import six
import logging

from . import base

LOG = logging.getLogger("devices")


class LocationManager(base.BaseManager):

    SCOPE = "identity/location"
