
import os
import logging
import decimal

LOG = logging.getLogger("manager.base")


from roboticeclient.common.client import BaseClient


class BaseManager(BaseClient):

    def __init__(self, **kwargs):
            
        self.host = kwargs.pop("host", os.getenv('ROBOTICE_HOST', '127.0.0.1'))
        self.port = kwargs.pop("port", os.getenv('ROBOTICE_PORT', 9753))
        self.protocol = kwargs.pop("protocol", os.getenv('ROBOTICE_PROTOCOL', "http")) 
        self.set_api()

def manager_factory(base_client=BaseManager):

    def initialize(self):
        pass

    def some_event(self):
        pass

    subclass_body_dict = {
        "initialize": initialize,
        "some_event": some_event
    }

    ManagerBase = type("ManagerBase", (base_client, ), {
            "initialize": initialize,
            "some_event": some_event
        })

    return ManagerBase