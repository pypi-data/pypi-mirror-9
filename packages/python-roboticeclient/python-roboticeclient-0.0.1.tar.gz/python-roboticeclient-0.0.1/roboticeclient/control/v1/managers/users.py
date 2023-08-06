
import sys
import six
import json
import logging

from . import base

LOG = logging.getLogger("users")


class UserManager(base.BaseManager):

    SCOPE = "identity/user"