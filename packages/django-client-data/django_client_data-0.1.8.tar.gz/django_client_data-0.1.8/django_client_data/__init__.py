__version__ = '0.1.8'


def set_client_data(request, **kwargs):
    """
    Set values to store in the JavaScript client data object.  Keys must be
    convertible to strings.
    """
    mapping = dict((str(k), v) for k, v in kwargs.items())
    request.client_data.update(mapping)
