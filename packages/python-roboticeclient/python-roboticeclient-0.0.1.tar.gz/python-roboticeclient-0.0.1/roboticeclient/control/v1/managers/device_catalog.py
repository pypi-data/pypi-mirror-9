
"""
Manager for device catalog
"""

import sys
import six
import logging

from . import base

LOG = logging.getLogger("devices")


class MetricManager(base.BaseManager):

    SCOPE = "device-catalog/metric"


class HostsManager(base.BaseManager):

    SCOPE = "device-catalog/host"


class DeviceCategoryManager(base.BaseManager):

    SCOPE = "device-catalog/category"


class BusPortManager(base.BaseManager):

    SCOPE = "device-catalog/bus-port"


class BusManager(base.BaseManager):

    SCOPE = "device-catalog/bus"


class ImageManager(base.BaseManager):

    SCOPE = "device-catalog/image"


class DeviceCatalogManager(base.BaseManager):

    SCOPE = "device-catalog"

    metrics = MetricManager()
    hosts = HostsManager()
    bus = BusManager()
    bus_ports = BusPortManager()
    images = ImageManager()
