
"""
Manager for devices
"""

import sys
import six
import logging

from control_client.robotice.managers import base

LOG = logging.getLogger(__name__)


class WorkerManager(base.RoboticeManager):

    def list(self):

        workers = []

        app = self.capp()

        events = app.events.State()

        _workers = app.control.inspect().stats()

        for worker_id, worker in six.iteritems(_workers):

            worker["id"] = worker_id
            workers.append(worker)

        return workers


workers = WorkerManager()
