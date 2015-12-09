import requests

class Client(object):
    def __init__(self, tornado_server):
        self.tornado_server = tornado_server

    @property
    def base_url(self):
        return "http://localhost:{}/api/v1".format(self.tornado_server.port)

    def request(self, method, url, **kwargs):
	
        headers = {}
        
        if method.lower() in ("put", "post"):
            headers["Content-type"] = "application/json"

        return requests.request(
            method, self.base_url + url,
            headers=headers, **kwargs
        )

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def create(self, url, **kwargs):
        return self.post(url, data=json.dumps(kwargs))

    def update(self, url, **kwargs):
        return self.put(url, data=json.dumps(kwargs))