from unicore.hub.client.base import BaseClient, BaseClientObject


class AppClient(BaseClient):
    base_path = '/apps'

    def create_app(self, data):
        new_data = self.post('', data=data)
        return App(self, new_data)

    def get_app(self, app_id):
        data = self.get('%s' % app_id)
        return App(self, data)

    def get_app_data(self, app_id):
        return self.get('%s' % app_id)

    def save_app_data(self, app_id, data):
        return self.put('%s' % app_id, data=data)

    def reset_app_key(self, app_id):
        data = self.put('%s/reset_key' % app_id, data='')
        return data['key']


class App(BaseClientObject):
    """
    A class that wraps an app's data dictionary and saves the data
    to the `unicore.hub` server.

    :param unicore.hub.client.AppClient app_client:
        A :py:class:`unicore.hub.client.AppClient` instance used to save
        and refresh the data dictionary.
    :param dict app_data:
        A dictionary containing app fields retrieved from the `unicore.hub`
        server.

    >>> app = app_client.create_app({'title': 'Foo'})
    >>> app.get('key')
    '1e82b117e30a7382d6ff327b00376cabda15ced3'
    >>> app.get('uuid')
    'f9e90e6b5a894c03b251df5b59c386d0'
    >>> app.get('title')
    'Foo'
    >>> app.get('groups')
    []
    >>> app.set('title', 'New Foo')
    >>> app.save()
    >>> app_key = app.reset_key()
    >>> app_key
    'eeaec8656792ae403c41265f45a33f18849a061e'
    >>>

    """

    def get(self, field):
        """
        Returns the value of an app field.

        :param str field:
            The name of the app field.
        :returns: str -- the value
        """
        return self.data[field]

    def set(self, field, value):
        """
        Sets the value of an app field.

        :param str field:
            The name of the app field. Trying to set immutable fields
            ``uuid`` or ``key`` will raise a ValueError.
        :param value:
            The new value of the app field.
        :raises: ValueError
        """
        if field == 'uuid':
            raise ValueError('uuid cannot be set')
        elif field == 'key':
            raise ValueError(
                'key cannot be set. Use \'reset_key\' method')
        else:
            self.data[field] = value

    def save(self):
        """
        Persists the app's data to the `unicore.hub` server.
        """
        self.client.save_app_data(self.get('uuid'), self.data)

    def refresh(self):
        """
        Reloads the app's data from the `unicore.hub` server.
        """
        self.data = self.client.get_app_data(self.get('uuid'))

    def reset_key(self):
        """
        Resets the app's key on the `unicore.hub` server.

        :returns: str -- the new key
        """
        new_key = self.client.reset_app_key(self.get('uuid'))
        self.data['key'] = new_key
        return new_key
