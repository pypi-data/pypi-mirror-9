
import os
import requests
import logging
import json
import decimal


LOG = logging.getLogger("robotice.client")

TOKEN_FORMAT = "  Token {0}"

from roboticeclient.common.horizon import HorizonClient


class BaseManager(HorizonClient):

    def __init__(self, **kwargs):

        if not hasattr(self, "host"):
            self.host = kwargs.pop("host", os.getenv('ROBOTICE_HOST', '127.0.0.1'))
        if not hasattr(self, "port"):
            self.port = kwargs.pop("port", os.getenv('ROBOTICE_PORT', 9753))
        if not hasattr(self, "protocol"):
            self.protocol = kwargs.pop(
                "protocol", os.getenv('ROBOTICE_PROTOCOL', "http"))
        self.set_api()