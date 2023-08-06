
import sys
import six
import json
import logging

from . import base

LOG = logging.getLogger("auth")


class AuthManager(base.BaseManager):

    SCOPE = "auth"

    def login(self, request, data):
        return self.request(
            request,
            '/{0}/login/'.format(self.SCOPE),
            'POST',
            data)

    def logout(self, request, data):
        return self.request(
            request,
            '/{0}/logout/'.format(self.SCOPE),
            'POST',
            data)