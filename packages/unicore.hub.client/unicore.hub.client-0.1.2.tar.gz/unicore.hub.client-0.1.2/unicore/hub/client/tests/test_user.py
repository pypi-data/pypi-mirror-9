from unittest import TestCase
from uuid import uuid4

import mock

from unicore.hub.client import User


class UserTestCase(TestCase):
    user_data = {
        'uuid': uuid4().hex,
        'username': 'foo_username',
        'app_data': {
            'display_name': 'foo_for_display',
            'age': 25,
            'favourite_colours': ['green', 'blue']
        }
    }

    def create_user(self, user_client=None, **data_overrides):
        data = self.user_data.copy()
        data.update(data_overrides)

        if not user_client:
            user_client = mock.Mock()

        return User(user_client, data)

    def test_set(self):
        user = self.create_user()

        # check that immutable fields cannot be set
        for field in ('username', 'uuid', 'app_data'):
            with self.assertRaisesRegexp(ValueError, 'cannot be set'):
                user.set(field, 'new_%s' % field)

        # check that app_data fields can be set
        user.set('favourite_fruit', 'peach')
        self.assertIn('favourite_fruit', user.data['app_data'])
        self.assertEqual(user.data['app_data']['favourite_fruit'], 'peach')

    def test_get(self):
        user = self.create_user()

        with self.assertRaises(KeyError):
            user.get('doesnotexist')

        # check that we can get immutable user field
        value_uuid = user.get('uuid')
        self.assertEqual(self.user_data['uuid'], value_uuid)

        # check that we can get user field nested in app_data
        value_display_name = user.get('display_name')
        self.assertEqual(
            self.user_data['app_data']['display_name'], value_display_name)

    def test_save(self):
        user = self.create_user()
        user.save()

        user.client.save_app_data.assert_called_with(
            self.user_data['uuid'], self.user_data['app_data'])

    def test_refresh(self):
        user = self.create_user()
        new_app_data = {
            'display_name': 'update_foo',
            'age': 'new_age',
            'favourite_colours': ['green'],
            'new_field': 'new_value'
        }
        self.assertNotEqual(user.data['app_data'], new_app_data)

        user.client.get_app_data = mock.Mock()
        user.client.get_app_data.return_value = new_app_data
        user.refresh()
        self.assertEqual(user.data['app_data'], new_app_data)
