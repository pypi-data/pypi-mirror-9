"""
Client library.

"""
import requests

from future import standard_library
standard_library.install_aliases()

from urllib.parse import urljoin

class ClientError(Exception):
    def __init__(self, response):
        self.response = response
        self.message = 'HTTP ' + str(response.status_code) + ' (' + str(response.content) + ')'

    def __str__(self):
        return self.message

class Client(object):
    """A file upload client. Takes the API endpoint URL and authorization
    token.

    """
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.token = token
        self._auth_headers = { 'Authorization': 'Bearer ' + str(self.token) }

    def upload(self, fobj):
        """Upload the contents of the file-like object fobj to the server and
        return the uuid corresponding to it. Raises ClientError on failure.

        """
        r = requests.post(
            urljoin(self.endpoint, 'upload'),
            files=dict(file=fobj),
            headers=self._auth_headers,
        )

        if r.status_code != 201:
            raise ClientError(r)

        return r.json()['id']

