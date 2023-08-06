import re
import json
from unittest import TestCase
from urllib import urlencode
from urlparse import urljoin, urlparse, parse_qs, urlunparse
from uuid import uuid4

import responses
import requests
from requests.auth import HTTPBasicAuth

from unicore.hub.client import AppClient, UserClient, ClientException


TICKET_INVALID_RESPONSE = json.dumps('no\n')


class BaseClientTestMixin(object):

    @classmethod
    def setUpClass(cls):
        cls.app_id = uuid4().hex
        cls.app_key = 'dakfjd042342cs'
        cls.host = 'http://localhost:8000'
        cls.login_callback_url = 'http://localhost:8080/callback'
        cls.client = cls.client_class(
            app_id=cls.app_id,
            app_key=cls.app_key,
            host=cls.host,
            login_callback_url=cls.login_callback_url
        )

    def check_request_basics(self, url):
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertEqual(request.url, url)
        basic_auth = HTTPBasicAuth(self.app_id, self.app_key)
        request_with_auth = basic_auth(requests.Request())
        self.assertEqual(request.headers['Authorization'],
                         request_with_auth.headers['Authorization'])

    def test_from_config(self):
        settings_new = {
            'unicorehub.host': 'http://localhost:8080',
            'unicorehub.app_id': 'fa84e670f9e9460fbf612c150dd06b45',
            'unicorehub.app_key': 'opW5Ba3KxMLcRmksOdje',
            'unicorehub.redirect_to_https': False,
            'unicorehub.login_callback_url': 'http://localhost:8080/callback'
        }
        settings_old = settings_new.copy()
        settings_old['unicorehub.app_password'] = settings_old[
            'unicorehub.app_key']
        del settings_old['unicorehub.app_key']

        for settings in (settings_new, settings_old):
            client = self.client_class.from_config(settings)
            self.assertEqual(client.settings, {
                'host': settings['unicorehub.host'],
                'app_id': settings['unicorehub.app_id'],
                'app_key': (settings.get('unicorehub.app_key') or
                            settings.get('unicorehub.app_password')),
                'redirect_to_https': settings['unicorehub.redirect_to_https'],
                'login_callback_url': settings['unicorehub.login_callback_url']
            })


class UserClientTestCase(BaseClientTestMixin, TestCase):
    client_class = UserClient

    @responses.activate
    def test_get_app_data(self):
        user_id = uuid4().hex
        user_app_data = {'display_name': 'foo'}
        url = urljoin(self.host, '/users/%s' % user_id)
        responses.add(
            responses.GET, url,
            body=json.dumps(user_app_data),
            status=200,
            content_type='application/json'
        )

        data = self.client.get_app_data(user_id)
        self.assertEqual(data, user_app_data)
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.GET, url, status=404)
        with self.assertRaisesRegexp(ClientException, 'HTTP 404'):
            self.client.get_app_data(user_id)

    @responses.activate
    def test_save_app_data(self):
        user_id = uuid4().hex
        user_app_data = {'display_name': 'foo'}
        url = urljoin(self.host, '/users/%s' % user_id)
        responses.add(
            responses.POST, url,
            body=json.dumps(user_app_data),
            status=200,
            content_type='application/json'
        )

        data = self.client.save_app_data(user_id, user_app_data)
        self.assertEqual(data, user_app_data)
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.POST, url, status=404)
        with self.assertRaisesRegexp(ClientException, 'HTTP 404'):
            self.client.save_app_data(user_id, {})

    @responses.activate
    def test_get_user(self):
        ticket = 'iamaticket'
        url = urljoin(
            self.host,
            '/sso/validate?%s' % urlencode({
                'service': self.login_callback_url,
                'ticket': ticket}))
        user_data = {
            'uuid': uuid4().hex,
            'username': 'foo_username',
            'app_data': {}
        }
        responses.add(
            responses.GET, re.compile(r'.*/sso/validate.*'),
            body=json.dumps(user_data),
            status=200,
            content_type='application/json'
        )

        user_obj = self.client.get_user(ticket)
        self.assertEqual(user_obj.data, user_data)
        self.check_request_basics(url)

        responses.reset()
        responses.add(
            responses.GET, re.compile(r'.*/sso/validate.*'),
            body=TICKET_INVALID_RESPONSE, status=200,
            content_type='application/json')
        with self.assertRaisesRegexp(ClientException, r'ticket.*is invalid'):
            self.client.get_user(ticket)

    def test_login_redirect_url(self):
        url = self.client.get_login_redirect_url(locale='tam_IN')
        parts = urlparse(url)
        params = parse_qs(parts.query)
        self.assertEqual(
            urlunparse(parts[:4] + ('', '')),
            urljoin(self.host.replace('http:', 'https:'), '/sso/login'))
        self.assertIn('service', params)
        self.assertEqual(params['service'][0], self.login_callback_url)
        self.assertIn('_LOCALE_', params)
        self.assertEqual(params['_LOCALE_'][0], 'tam_IN')
        self.assertIn(
            urlencode({'service': 'http://example.com'}),
            self.client.get_login_redirect_url('http://example.com'))

        settings_no_callback = self.client.settings.copy()
        del settings_no_callback['login_callback_url']
        client_no_callback = UserClient(**settings_no_callback)
        with self.assertRaisesRegexp(
                ValueError, 'no login_callback_url provided'):
            client_no_callback.get_login_redirect_url()
        with self.assertRaisesRegexp(
                ValueError, 'login_callback_url must be absolute'):
            client_no_callback.get_login_redirect_url('/callback')

        settings_disable_https = self.client.settings.copy()
        settings_disable_https['redirect_to_https'] = False
        client_disable_https = UserClient(**settings_disable_https)
        url = client_disable_https.get_login_redirect_url()
        parts = urlparse(url)
        self.assertEqual(
            urlunparse(parts[:4] + ('', '')), urljoin(self.host, '/sso/login'))


class AppClientTestCase(BaseClientTestMixin, TestCase):
    client_class = AppClient

    @responses.activate
    def test_create_app(self):
        url = urljoin(self.host, '/apps')
        app_data = {
            'title': 'Foo',
            'groups': ['group:apps_manager'],
            'url': 'http://www.example.com'
        }
        app_data_complete = app_data.copy()
        app_data_complete.update({
            'uuid': uuid4().hex,
            'key': 'key'})
        responses.add(
            responses.POST, url,
            body=json.dumps(app_data_complete),
            status=201,
            content_type='application/json'
        )

        app = self.client.create_app(app_data)
        self.assertEqual(app.data, app_data_complete)
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.POST, url, status=400)
        with self.assertRaisesRegexp(ClientException, 'HTTP 400'):
            self.client.create_app(app_data)

    @responses.activate
    def test_get_app(self):
        app_data = {
            'uuid': uuid4().hex,
            'title': 'Foo',
            'groups': ['group:apps_manager']
        }
        url = urljoin(self.host, '/apps/%s' % app_data['uuid'])
        responses.add(
            responses.GET, url,
            body=json.dumps(app_data),
            status=200,
            content_type='application/json'
        )

        app = self.client.get_app(app_data['uuid'])
        self.assertEqual(app.data, app_data)
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.GET, url, status=404)
        with self.assertRaisesRegexp(ClientException, 'HTTP 404'):
            self.client.get_app(app_data['uuid'])

    @responses.activate
    def test_get_app_data(self):
        app_data = {
            'uuid': uuid4().hex,
            'title': 'Foo',
            'groups': ['group:apps_manager']
        }
        url = urljoin(self.host, '/apps/%s' % app_data['uuid'])
        responses.add(
            responses.GET, url,
            body=json.dumps(app_data),
            status=200,
            content_type='application/json'
        )

        data = self.client.get_app_data(app_data['uuid'])
        self.assertEqual(data, app_data)
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.GET, url, status=404)
        with self.assertRaisesRegexp(ClientException, 'HTTP 404'):
            self.client.get_app_data(app_data['uuid'])

    @responses.activate
    def test_save_app_data(self):
        app_data = {
            'uuid': uuid4().hex,
            'title': 'Foo',
            'groups': ['group:apps_manager']
        }
        url = urljoin(self.host, '/apps/%s' % app_data['uuid'])
        responses.add(
            responses.PUT, url,
            body=json.dumps(app_data),
            status=200,
            content_type='application/json'
        )

        data = self.client.save_app_data(app_data['uuid'], app_data)
        self.assertEqual(data, app_data)
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.PUT, url, status=404)
        with self.assertRaisesRegexp(ClientException, 'HTTP 404'):
            self.client.save_app_data(app_data['uuid'], app_data)

    @responses.activate
    def test_reset_app_key(self):
        app_data = {
            'uuid': uuid4().hex,
            'title': 'Foo',
            'url': 'http://www.example.com',
            'groups': ['group:apps_manager'],
            'key': 'key'
        }
        url = urljoin(self.host, '/apps/%s/reset_key' % app_data['uuid'])
        responses.add(
            responses.PUT, url,
            body=json.dumps(app_data),
            status=200,
            content_type='application/json'
        )

        key = self.client.reset_app_key(app_data['uuid'])
        self.assertEqual(key, 'key')
        self.check_request_basics(url)

        responses.reset()
        responses.add(responses.PUT, url, status=404)
        with self.assertRaisesRegexp(ClientException, 'HTTP 404'):
            self.client.reset_app_key(app_data['uuid'])
