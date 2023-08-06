

from roboticeclient.common import importutils


def Client(version=1, **kwargs):
    """Factory function to create a new identity service client.
    :param tuple version: The required version of the identity API.
    :param kwargs: Additional arguments are passed through to the client
                   that is being created.
    :returns: New robotice client object
              (roboticeclient.v1.Client).
    :raises roboticeclient.exceptions.DiscoveryFailure: if the server's
                                                        response is invalid
    """

    mod = importutils.import_module(
        "roboticeclient.robotice.v%s.base" % version)

    client = mod.RoboticeClient(**kwargs)

    return client
