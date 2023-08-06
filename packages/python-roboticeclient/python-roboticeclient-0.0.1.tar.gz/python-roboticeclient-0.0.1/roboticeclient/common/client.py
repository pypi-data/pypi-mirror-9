
import os
import requests
import logging
import json
import decimal

from requests.exceptions import Timeout

LOG = logging.getLogger("client.base")

TOKEN_FORMAT = "  Token {0}"

# decimal serialization


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


class BaseClientMixin(object):

    def list(self):
        return self.request(
            '/%s/' % self.SCOPE,
            'GET')

    def get(self, request, id):
        return self.request(
            request,
            '/{0}/{1}/'.format(self.SCOPE, id),
            'GET')


    def create(self, request, data):
        return self.request(
            request,
            '/{0}/'.format(self.SCOPE),
            'PUT',
            data)

    def update(self, request, id, data):
        return self.request(
            request,
            '/{0}/{1}/'.format(self.SCOPE, id),
            'POST',
            data)

    def delete(self, request, id):
        return self.request(
            request,
            '/{0}/{1}/'.format(self.SCOPE, id),
            'DELETE')

class ClientException(Exception):

    """
    The base exception class for all exceptions this library raises.
    """

    def __init__(self, code, message=None, details=None):
        self.code = code
        self.message = message or self.__class__.message
        self.details = details

    def __str__(self):
        return "%s (HTTP %s)" % (self.message, self.code)

    message = "HTTP error"


class BaseClient(BaseClientMixin):

    api_prefix = '/api' # /api/v1 etc

    def __init__(self, **kwargs):

        self.host = kwargs.pop("host", os.getenv('ROBOTICE_HOST', '127.0.0.1'))
        self.port = kwargs.pop("port", os.getenv('ROBOTICE_PORT', 9753))
        self.protocol = kwargs.pop(
            "protocol", os.getenv('ROBOTICE_PROTOCOL', "http"))
        self.set_api()

    def request(self, path, method="GET", params={}):
        headers = {}

        LOG.debug("%s - %s%s - %s" % (method, self.api, path, params))

        if method == "GET":
            request = requests.get('%s%s' % (self.api, path), headers=headers)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            request = requests.post('%s%s' % (self.api, path), data=json.dumps(
                params, default=decimal_default), headers=headers)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            request = requests.put('%s%s' % (self.api, path), data=json.dumps(
                params, default=decimal_default), headers=headers)

        if request.status_code in (200, 201):
            result = request.json()
            if "error" in result:
                msg = result.get("error")
                # populate exception
                LOG.error(msg)
            else:
                return result
            return result
        else:
            msg = "url: %s%s, method: %s, status: %s" % (
                self.api, path, method, request.status_code)
            LOG.error(msg)
            return []

    def get_location(self, request):
        """must return location queue, for now tenant name will be used
        """
        return request.user.tenant_name

    def set_api(self):
        self.api = '%s://%s:%s%s' % (getattr(self, "protocol", "http"), getattr(
            self, "host", "127.0.0.1"), getattr(self, "port"), getattr(self, "api_prefix", "/api"))
