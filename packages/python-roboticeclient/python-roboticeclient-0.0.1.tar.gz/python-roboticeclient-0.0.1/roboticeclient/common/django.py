from __future__ import absolute_import
import os
import requests
import logging
import json
import decimal

from django.conf import settings
from django.contrib import messages

from roboticeclient.common.client import BaseClient
from roboticeclient.utils.dotdict import list_to_dotdict

LOG = logging.getLogger("client.base")

TOKEN_FORMAT = "  Token {0}"


class DjangoClient(BaseClient):

    """use django settings for configuration and provide some additional messages
    ROBOTICE_HOST default is localhost
    ROBOTICE_PORT default is 9753
    ROBOTICE_PROTOCOL default is http
    """

    api_prefix = '/api' # /api/v1 etc

    location = False

    auth_token = False

    def __init__(self, **kwargs):
        super(DjangoClient, self).__init__(**kwargs)

        try:
            from local_settings import ROBOTICE_HOST, ROBOTICE_PORT
            self.host = ROBOTICE_HOST
            self.port = ROBOTICE_PORT
        except Exception, e:
            LOG.error(str(e))

        self.set_api()

    def request(self, request, path, method="GET", params={}):
        headers = {}

        _request = request
        self.set_api()
        LOG.debug("%s - %s%s - %s"%(method,self.api,path,params))
        
        if method == "GET":
            request = requests.get('%s%s' % (self.api, path), headers=headers)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            request = requests.post('%s%s' % (self.api, path),data=json.dumps(params, default=decimal_default),headers=headers)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            request = requests.put('%s%s' % (self.api, path),data=json.dumps(params, default=decimal_default),headers=headers)
        elif method == "DELETE":
            request = requests.delete('%s%s' % (self.api, path),data=json.dumps(params, default=decimal_default),headers=headers)
        
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
                msg = "url: %s%s, method: %s, status: %s" % (self.api, path, method, request.status_code)
            else:
                msg = "Unexpected exception."
            messages.error(_request, msg)
            return []

    def list(self, request):
        return self.request(
            request,
            '/%s' % self.SCOPE,
            'GET')