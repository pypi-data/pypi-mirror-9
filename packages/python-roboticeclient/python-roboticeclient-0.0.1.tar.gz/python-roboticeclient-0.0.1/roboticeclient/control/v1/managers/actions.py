
"""
Manager for devices
"""

import sys
import six
import logging

from . import base

LOG = logging.getLogger(__name__)


class ActionManager(base.BaseManager):

    SCOPE = "action"

    def do(self, request, id):
        return self.request(
            request,
            '/{0}/{1}/do'.format(self.SCOPE, id),
            'POST')
