import os
import json
from urlparse import urljoin, urlparse, urlunparse

import requests
from requests.auth import HTTPBasicAuth

from unicore.hub.client.utils import client_from_config


class ClientException(Exception):
    pass


class BaseClient(object):

    def __init__(self, **settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(
            settings['app_id'],
            settings['app_key'])
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        self.host = settings['host']

    @property
    def base_path(self):
        return getattr(self, 'base_path', '')

    def _make_url(self, path, use_https=False):
        path = os.path.join(self.base_path, path) if path else self.base_path
        host = self.host

        if use_https and not self.host.startswith('https'):
            parts = urlparse(self.host)
            host = urlunparse(('https', ) + parts[1:])

        return urljoin(host, path)

    def _request(self, method, path, *args, **kwargs):
        return self._request_no_parse(method, path, *args, **kwargs).json()

    def _request_no_parse(self, method, path, *args, **kwargs):
        kwargs = kwargs.copy()
        use_https = kwargs.pop('use_https', False)
        url = self._make_url(path, use_https=use_https)
        resp = self.session.request(method, url, *args, **kwargs)

        if resp.status_code not in (200, 201, 204):
            raise ClientException('HTTP %s: %s' %
                                  (resp.status_code, resp.content))

        return resp

    def get(self, path, *args, **kwargs):
        return self._request('get', path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        kwargs['data'] = json.dumps(kwargs['data'])
        return self._request('post', path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        kwargs['data'] = json.dumps(kwargs['data'])
        return self._request('put', path, *args, **kwargs)

    @classmethod
    def from_config(cls, config, **kwargs):
        return client_from_config(cls, config, **kwargs)


class BaseClientObject(object):

    def __init__(self, client, data):
        self.client = client
        self.data = data

    def get(self, field):
        raise NotImplementedError

    def set(self, field, value):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError
