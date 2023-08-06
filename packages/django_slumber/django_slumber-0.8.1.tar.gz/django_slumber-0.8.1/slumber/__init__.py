"""
    Slumber is a RESTful client/server implementation that makes it simple
    to make use of Django models in a RESTful manner.
"""
from slumber.connector import Client
from slumber.configuration import configure


# In order to allow mocking of the Slumber client instance we need an extra
# level of indirection to give us something we can mock. The below code
# provides that.

# Create a location for where to put the real client
_client = Client()

class _ClientProxy(object):
    """A forwarder for the real client.
    """
    def __getattr__(self, name):
        return getattr(_client, name)

# The client other code will import will always forward to the mockable
# _client instance.
# This is exactly the name we want to use here
# pylint: disable=C0103
client = _ClientProxy()


def data_link(instance, *args, **kwargs):
    """Convenience function to return the default 'data' operation link
    for an instance.
    """
    if instance is None:
        return None
    else:
        operation = type(instance).slumber_model.operations['data']
        return operation(instance, *args, **kwargs)

