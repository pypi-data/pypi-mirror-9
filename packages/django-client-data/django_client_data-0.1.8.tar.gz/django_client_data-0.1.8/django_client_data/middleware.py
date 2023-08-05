class ClientDataDict(dict):
    def __init__(self, **kwargs):
        self.include_standard_values = True
        super(ClientDataDict, self).__init__(**kwargs)

    def disable_standard_values(self):
        self.include_standard_values = False


class ClientDataMiddleware(object):
    def process_request(self, request):
        request.client_data = ClientDataDict()
