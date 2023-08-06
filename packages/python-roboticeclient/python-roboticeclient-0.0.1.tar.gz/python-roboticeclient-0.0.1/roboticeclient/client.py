

from roboticeclient.common import importutils


def Client(version=1, type="robotice", **kwargs):
    """Factory function to create a new identity service client.
    :param tuple version: The required version of the identity API.
    :param kwargs: Additional arguments are passed through to the client
                   that is being created.
    :returns: New robotice client object
              (roboticeclient.v1.Client).
    :raises roboticeclient.exceptions.DiscoveryFailure: if the server's
                                                        response is invalid
    """

    try:

        mod = importutils.import_module(
            "roboticeclient.%s.client" % (type))

        client = mod.Client(version, **kwargs)

    except Exception, e:
        raise e

    return client
