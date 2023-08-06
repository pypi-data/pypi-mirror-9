
"""
Manager for devices
"""

import sys
import six
import logging

import base

LOG = logging.getLogger("devices")


class DeviceManager(base.RoboticeManager):

    SCOPE = "device"

    def real_devices(self, request):
        return self.request(
            request,
            '/real-device/',
            'GET')

    def real_device_create(self, request, data):
        return self.request(
            request,
            '/real-device/',
            'PUT',
            data)

    def real_device_update(self, request, id, data):
        return self.request(
            request,
            '/real-device/%s/' % id,
            'POST',
            data)

    def real_device_get(self, request, id):
        return self.request(
            request,
            '/real-device/%s/' % id,
            'GET')

devices = DeviceManager()
