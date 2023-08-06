
from __future__ import absolute_import

import os
import requests
import logging
import json
import decimal

from horizon import messages
from django.conf import settings

from roboticeclient.common.django import DjangoClient
from roboticeclient.utils.dotdict import list_to_dotdict

from roboticeclient.exceptions import Unauthorized, BadRequest, ClientException

LOG = logging.getLogger("client.base")

TOKEN_FORMAT = "  Token {0}"


class HorizonClient(DjangoClient):

    """use Openstack Horizon settings for configuration and provide some additional messages
    ROBOTICE_HOST default is localhost
    ROBOTICE_PORT default is 9753
    ROBOTICE_PROTOCOL default is http

    we use tenant_name as location
    """

    def __init__(self, **kwargs):
        super(DjangoClient, self).__init__(**kwargs)

        try:
            from openstack_dashboard.local.local_settings import ROBOTICE_HOST, ROBOTICE_PORT
            self.host = ROBOTICE_HOST
            self.port = ROBOTICE_PORT
        except Exception, e:
            LOG.error(str(e))

        self.set_api()

    def request(self, request, path, method="GET", params={}):
        headers = {}

        _request = request
        self.set_api()
        LOG.debug("%s - %s%s - %s" % (method, self.api, path, params))

        if hasattr(_request.user, "location"):
            try:
                token = _request.session['token'].id
                headers["Authorization"] = TOKEN_FORMAT.format(token)
            except Exception, e:
                raise e

        if method == "GET":
            request = requests.get('%s%s' % (self.api, path), headers=headers)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            request = requests.post(
                '%s%s' % (self.api, path), data=json.dumps(params), headers=headers)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            request = requests.put(
                '%s%s' % (self.api, path), data=json.dumps(params), headers=headers)
        elif method == "DELETE":
            request = requests.delete(
                '%s%s' % (self.api, path), data=json.dumps(params), headers=headers)

        if request.status_code in (200, 201):
            result = request.json()
            if "error" in result:
                msg = result.get("error")
                # populate exception
                messages.error(_request, msg)
                if settings.DEBUG:
                    raise Exception(msg)
            else:
                converted_dict = list_to_dotdict(result)
                return converted_dict
            return result
        else:
            if getattr(settings, "DEBUG", False):
                msg = "url: %s%s, method: %s, status: %s" % (
                    self.api, path, method, request.status_code)
            else:
                msg = "Unexpected exception."
            if request.status_code == 401:
                raise Unauthorized
            if request.status_code == 400:
                raise BadRequest
            messages.error(_request, msg)
            raise ClientException("Unhandled response status %s" % request.status_code)

    def get_location(self, request):
        """must return location queue, for now tenant name will be used
        """
        return request.user.location
