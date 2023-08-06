
"""
"""

import sys
import six
import logging

from . import base

LOG = logging.getLogger("common")


class ConstManager(base.BaseManager):

    SCOPE = "common"
