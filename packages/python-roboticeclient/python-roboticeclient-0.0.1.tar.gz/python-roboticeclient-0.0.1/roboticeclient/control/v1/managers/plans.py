
"""
Manager for plans
"""

import sys
import six
import json
import logging

import base

LOG = logging.getLogger("systems")


class PlanManager(base.BaseManager):

    SCOPE = "plan"
