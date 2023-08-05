

class SirenInvalid(Exception):
    def __init__(self, message, data=None):
        Exception.__init__(self, message)
        self.data = data


class SirenObject(object):
    def __getstate__(self):
        '''Ensure that client does not get pickled'''
        state = self.__dict__.copy()
        if 'client' in state:
            state['client'] = None
        return state


class SirenActions(SirenObject, dict):
    def __init__(self, client, data):
        self.client = client
        self.data = data
        for action in data:
            self[action['name']] = action

    def __repr__(self):
        return '<SirenActions (%s)>' % ','.join(self.keys())

    def __getitem__(self, item):
        value = dict.__getitem__(self, item)
        if not isinstance(value, SirenAction):
            value = SirenAction(self.client, dict.__getitem__(self, item))
            self[item] = value
        return value

    def items(self):
        return [(key,self[key]) for key in self]



class SirenEntities(SirenObject, list):
    def __init__(self, client, data):
        self.client = client
        self.data = data
        for entity in data:
            self.append(SirenEntity(client, entity))

    def __repr__(self):
        return '<SirenEntities (%d)>' % len(self)


class SirenLinks(SirenObject, dict):
    def __init__(self, client, data):
        self.client = client
        self.data = data
        for link in data:
            for rel in link['rel']:
                rel = self.client.convert_rel(rel)
                if rel in self:
                    raise SirenInvalid('The rel was not unique: %s' % rel)
                self[rel] = link['href']

    def __repr__(self):
        return '<SirenLinks (%s)>' % ','.join(self.keys())

    def __getitem__(self, item):
        uri = dict.__getitem__(self, item)
        return self.client.follow(uri)

    def items(self):
        return [(key,self[key]) for key in self]


class SirenAction(SirenObject):
    def __init__(self, client, data):
        self.client = client
        self.data = data
        self.values = {}
        for field in self.fields:
            if 'value' in field:
                self.values[field['name']] = field['value']

    def __repr__(self):
        return '<SirenAction (%s)>' % ','.join([f['name']
                                                for f in self.fields])

    def __call__(self, **kwargs):
        return self.call(**kwargs)

    def populate(self, entity):
        for field in self.fields:
            value = entity.get(field['name'], None)
            if value is not None:
                self.values[field['name']] = value

    @property
    def fields(self):
        return self.data.get('fields', [])

    @property
    def content_type(self):
        return self.data.get('type', 'application/x-www-form-urlencoded')

    @property
    def method(self):
        return self.data.get('method', 'GET').lower()

    def call(self, **kwargs):
        request_args = {
            'data': None,
            'method': self.method,
            'url': self.data['href'],
            }
        self.values.update(kwargs)
        # 99.99% of API's will probably want these in the query string
        if self.method in ['get', 'delete']:
            request_args['params'] = self.values
        else:
            request_args['headers'] = {'content-type': self.content_type}
            request_args['data'] = self.values
        return SirenEntity(client=self.client,
                           data=self.client.request(**request_args))


class SirenEntity(SirenObject, dict):
    def __init__(self, client, data):
        self.siren = {
            'entities': None,
            'links': None,
            'actions': None,
        }
        self.client = client
        self.data = data

        try:
            properties = data.get('properties', {})
            dict.__init__(self, **properties)
        except AttributeError, e:
            raise SirenInvalid('Data is not a valid Siren Representation', data)

    @property
    def title(self):
        return self.data.get('title', None)

    @property
    def class_(self):
        return self.data.get('class', [])

    @property
    def uri(self):
        self_rel = None
        for link in self.data.get('links', []):
            if self.client.config['self_rel'] in link['rel']:
                self_rel = link['href']
        if self_rel is None and 'href' in self.data:
            return self.data['href']
        return self_rel

    @property
    def rel(self):
        rels = self.data.get('rel', None)
        if rels is None:
            return None
        return [self.client.convert_rel(rel) for rel in rels]

    def is_subentity(self):
        return 'rel' in self.data

    def is_stub(self):
        return 'href' in self.data

    def refresh(self):
        if self.uri is None:
            raise SirenInvalid('Entity cannot refresh as it has no URI')

        self.clear()
        self.data = self.client.request(self.uri)
        self.siren = {
            'entities': None,
            'links': None,
            'actions': None,
        }
        self.update(self.data.get('properties', {}))

    def __repr__(self):
        return '<SirenEntity (class:%s) (%s)>' % (','.join(self.class_),
                                                  self.uri)

    def _make_and_cache(self, name, factory):
        obj = self.siren.get(name, None)
        if obj is None:
            obj = factory(self.client, 
                          self.data.get(name, []))
            self.siren[name] = obj
        return obj

    @property
    def links(self):
        return self._make_and_cache('links', SirenLinks)

    @property
    def actions(self):
        return self._make_and_cache('actions', SirenActions)

    @property
    def entities(self):
        return self._make_and_cache('entities', SirenEntities)

