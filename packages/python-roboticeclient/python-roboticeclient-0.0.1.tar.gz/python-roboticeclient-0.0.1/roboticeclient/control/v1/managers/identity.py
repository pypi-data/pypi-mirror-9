
import sys
import six
import json
import logging

from . import base

LOG = logging.getLogger("users")

from .users import UserManager
from .auth import AuthManager


class IdentityManager(base.BaseManager):

    SCOPE = "identity"

    # PROXY
    users = UserManager()
    auth = AuthManager()