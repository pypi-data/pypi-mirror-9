
"""
Manager for plans
"""

import sys
import six
import json
import logging

from . import base

LOG = logging.getLogger("systems")


class HostManager(base.BaseManager):

    SCOPE = "host"
