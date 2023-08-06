
"""
Manager for plans
"""

import sys
import six
import json
import logging

from celery import states
from celery import Celery
from celery.result import AsyncResult
from celery.backends.base import DisabledBackend

from control_client.robotice.managers import base

LOG = logging.getLogger("systems")


class PlanManager(base.RoboticeManager):

    SCOPE = "plan"

plans = PlanManager()
