
import requests
import logging
import json
import decimal

from requests.exceptions import Timeout

from .managers.actions import ActionManager
from .managers.devices import DeviceManager
from .managers.systems import SystemManager

log = logging.getLogger(__name__)

TOKEN_FORMAT = "  Token {0}"


class RoboticeClient(object):

    def __init__(self, **kwargs):

        self.systems = SystemManager(**kwargs)
        self.devices = DeviceManager(**kwargs)
        self.actions = ActionManager(**kwargs)

    def model_devices(self, request):
        return self.request(
            request,
            '/model-device/',
            'GET')

    def host_list(self, request):
        return self.request(
            request,
            '/host/',
            'GET')

    def system_devices(self, request):
        return self.request(
            request,
            '/system-device/',
            'GET')

    def locations(self, request):
        return self.request(
            request,
            '/location/',
            'GET')

    def plan_list(self, request):
        return self.request(
            request,
            '/plan/',
            'GET')