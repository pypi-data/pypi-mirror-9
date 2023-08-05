from .compat import json
from .entity import SirenEntity

DEFAULT_CONFIG = {
    'rel_base': None,
    'loads': None,
    'dumps': None,
    'self_rel': 'self',
    'raise_for_status': True,
}


class SirenClient(object):

    def __init__(self, session, config=None):
        self.config = {}
        self.config.update(DEFAULT_CONFIG)
        if config is not None:
            self.config.update(config)
        self.session = session

    def __getstate__(self):
        '''Prevent any accidental pickling of this object'''
        raise ValueError, 'SirenClient should not be pickled'

    def request(self, url, method='get', **kwargs):
        if 'data' in kwargs:
            content_type = kwargs.get('headers', {}).get('content-type', None)
            kwargs['data'] = self.dumps(content_type, kwargs['data'])


        request = getattr(self.session, method)
        response = request(url, **kwargs)
        if response.text is None or len(response.text) == 0:
            if 'location' in response.headers:
                return self.request(url=response.headers['location'], method='get')
            elif method.lower() != 'get':
                return self.request(url=url, method='get')

        if self.config['raise_for_status']:
            response.raise_for_status()
        return self.loads(response.headers.get('content-type', None),
                          response.content)

    def follow(self, url, method='get', **kwargs):
        return SirenEntity(self, self.request(url, method=method, **kwargs))

    def dumps(self, content_type, obj):
        if self.config['dumps'] is not None:
            return self.config['dumps'](content_type, obj)
        if content_type == 'application/json':
            return json.dumps(obj)
        return obj

    def loads(self, content_type, s):
        if self.config['loads'] is not None:
            return self.config['loads'](content_type, s)
        if content_type == 'application/json':
            return json.loads(s)
        # Lets try JSON anyway, as it is going to be the most common
        try:
            return json.loads(s)
        except ValueError:
            return s

    def convert_rel(self, value):
        rel_base = self.config.get('rel_base')
        if rel_base is None:
            return value

        if value[:len(rel_base)] != rel_base:
            return value
        return value[len(rel_base):]
