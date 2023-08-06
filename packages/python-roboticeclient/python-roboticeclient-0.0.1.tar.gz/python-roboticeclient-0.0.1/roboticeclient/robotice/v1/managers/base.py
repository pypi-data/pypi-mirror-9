
import os
import logging
import json
import decimal


LOG = logging.getLogger("robotice.client")

from roboticeclient.common.manager import BaseManager


class RoboticeManager(BaseManager):

    api_prefix = ''  # /api/v1 etc

    def __init__(self, **kwargs):

        self.host = kwargs.pop("host", os.getenv('ROBOTICE_HOST', '127.0.0.1'))
        self.port = kwargs.pop("port", os.getenv('ROBOTICE_PORT', 8004))
        self.protocol = kwargs.pop(
            "protocol", os.getenv('ROBOTICE_PROTOCOL', "http"))
        self.set_api()
