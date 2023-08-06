from urlparse import urlparse


PROTOCOL_TO_PORT = {
    'http': 80,
    'https': 443,
}


def client_from_config(
        client_cls, configuration, prefix='unicorehub.', **kwargs):
    settings = dict((key[len(prefix):], value)
                    for key, value in configuration.iteritems()
                    if key.startswith(prefix))
    settings.update(kwargs)

    # password renamed to key - don't break old configs
    if 'app_password' in settings:
        settings['app_key'] = settings['app_password']
        del settings['app_password']

    return client_cls(**settings)


def same_origin(url1, url2):
    ''' Return True if the urls have the same origin, else False.
    Copied from Django:
    https://github.com/django/django/blob/master/django/utils/http.py#L255
    '''
    p1, p2 = urlparse(url1), urlparse(url2)
    try:
        o1 = (p1.scheme, p1.hostname, p1.port or PROTOCOL_TO_PORT[p1.scheme])
        o2 = (p2.scheme, p2.hostname, p2.port or PROTOCOL_TO_PORT[p2.scheme])
        return o1 == o2
    except (ValueError, KeyError):
        return False
