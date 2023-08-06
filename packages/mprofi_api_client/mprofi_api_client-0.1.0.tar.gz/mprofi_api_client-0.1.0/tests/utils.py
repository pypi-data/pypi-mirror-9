from mprofi_api_client.packages.requests.models import Response


class FakeSession(object):

    url = None
    headers = None
    data = None
    json = None

    def __init__(self):
        self.headers = {}

    def post(self, url, data=None, json=None, **kwargs):
        self.url = url
        self.data = data
        self.json = json
        resp = Response()
        resp.status_code = 200
        resp._content = '{"id": 1, "result": [{"id": 1}]}'
        return resp
