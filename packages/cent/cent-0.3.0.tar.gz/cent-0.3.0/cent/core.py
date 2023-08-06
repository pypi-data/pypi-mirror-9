# coding: utf-8
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

try:
    from urllib import urlencode
except ImportError:
    # python 3
    # noinspection PyUnresolvedReferences
    from urllib.parse import urlencode

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

import six
import hmac
import json
from hashlib import sha256


def generate_token(secret_key, project_id, user_id, timestamp, info=None):
    """
    When client from browser wants to connect to Centrifuge he must send his
    user ID and ID of project. To validate that data we use HMAC to build
    token.
    """
    if info is None:
        info = json.dumps({})
    sign = hmac.new(six.b(str(secret_key)), digestmod=sha256)
    sign.update(six.b(project_id))
    sign.update(six.b(user_id))
    sign.update(six.b(timestamp))
    sign.update(six.b(info))
    token = sign.hexdigest()
    return token


def generate_channel_sign(secret_key, client_id, channel, info=None):
    """
    Generate HMAC sign for private channel subscription
    """
    if info is None:
        info = json.dumps({})

    auth = hmac.new(six.b(str(secret_key)), digestmod=sha256)
    auth.update(six.b(str(client_id)))
    auth.update(six.b(str(channel)))
    auth.update(six.b(info))
    return auth.hexdigest()


def generate_api_sign(secret_key, project_id, encoded_data):
    """
    Generate HMAC sign for api request
    """
    sign = hmac.new(six.b(str(secret_key)), digestmod=sha256)
    sign.update(six.b(project_id))
    sign.update(encoded_data)
    return sign.hexdigest()


class Client(object):

    def __init__(self, address, project_id, secret_key,
                 timeout=2, send_func=None, json_encoder=None, **kwargs):
        self.address = address
        self.project_id = project_id
        self.secret_key = secret_key
        self.timeout = timeout
        self.send_func = send_func
        self.json_encoder = json_encoder
        self.kwargs = kwargs
        self.messages = []

    def prepare_url(self):
        return '/'.join([self.address.rstrip('/'), self.project_id])

    def sign_encoded_data(self, encoded_data):
        return generate_api_sign(self.secret_key, self.project_id, encoded_data)

    def prepare(self, data):
        url = self.prepare_url()
        encoded_data = six.b(json.dumps(data, cls=self.json_encoder))
        sign = self.sign_encoded_data(encoded_data)
        return url, sign, encoded_data

    def add(self, method, params):
        data = {
            "method": method,
            "params": params
        }
        self.messages.append(data)

    def send(self, method=None, params=None):
        if method and params is not None:
            self.add(method, params)
        messages = self.messages[:]
        self.messages = []
        if self.send_func:
            return self.send_func(*self.prepare(messages))
        return self._send(*self.prepare(messages))

    def _send(self, url, sign, encoded_data):
        """
        Send a request to a remote web server using HTTP POST.
        """
        req = Request(url)
        try:
            response = urlopen(
                req,
                six.b(urlencode({'sign': sign, 'data': encoded_data})),
                timeout=self.timeout
            )
        except Exception as e:
            return None, e
        else:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            return result, None
