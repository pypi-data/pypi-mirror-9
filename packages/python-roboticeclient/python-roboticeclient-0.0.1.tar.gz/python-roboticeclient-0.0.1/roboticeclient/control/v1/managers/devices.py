
"""
Manager for devices
"""

import sys
import six
import logging

from . import base

LOG = logging.getLogger("devices")


class RealDeviceManager(base.BaseManager):

    SCOPE = "host/real-device"


class ModelDeviceManager(base.BaseManager):

    SCOPE = "plan/model-device"


class SystemDeviceManager(base.BaseManager):

    SCOPE = "system/system-device"
