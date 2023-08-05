from threading import local

from floraconcierge.client import ApiClient

_active = local()


def get_apiclient():
    """
    :rtype: ApiClient
    """
    if not hasattr(_active, "value"):
        raise ValueError('Not activated any apiclient. Please ``activate`` apiclient first')

    client = _active.value
    assert isinstance(_active.value, ApiClient)

    return client


def activate(client):
    """
    Sets the api client for the current thread.

    The ``timezone`` argument must be an instance of a ApiClient subclass
    """
    assert isinstance(client, ApiClient), 'ApiClient object required'
    _active.value = client


def deactivate():
    """
    Unsets the api client for the current thread.
    """
    if hasattr(_active, "value"):
        del _active.value


class override(object):
    """
    Temporarily set the api client for the current thread.
    """

    def __init__(self, client):
        self.client = client
        self.old_client = getattr(_active, 'value', None)

    def __enter__(self):
        if self.client is None:
            deactivate()
        else:
            activate(self.client)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.old_client is None:
            deactivate()
        else:
            _active.value = self.old_client
