Siren Client for Python
=======================


A generic client for consuming Hypermedia API's which utilise
[Siren](https://github.com/kevinswiber/siren) for the entity schema.

The client consumes the Siren and creates objects which represent the various
Siren Objects. This library does not provide a transport mechanism to access the
API but is designed to work with a
[requests](http://docs.python-requests.org/en/latest/) session.

Authentication is managed by the session manager provided to the the Siren
client. Usage patterns below.


## Installing

The library is available to install using pip:

    $ pip install siren-client

Alternatively, you can clone this package and install it yourself.


## Getting Started

The client is designed to allow you to traverse the data in the API, without
having to worry about requests or URL construction. You simply need to provide
the first object with a url:

```python
import siren_client

entity = siren_client.get('http://some.siren-api.com/')
```

Each Siren Entity provided some introspection so that you can quickly see what
the entity is.

```python
print entity
```

All of siren concepts are available as Python constructs.

### Basic Siren Attributes

```python
print entity.uri
print entity.class_
print entity.rel  # Generally only if it is a sub-entity
```

### Siren Properties are available on the entity

```python
print entity['Name']
```

### An Entity can be 'refreshed' from the server

```python
entity.refresh()
```

### Following Siren links

```python
print entity.links
second_entity = entity.links['some-link']
```

### Using Siren Actions

```python
print entity.actions
print entity.actions['next']

collection = entity.actions['next']()

# You can pass any parameters to an action

collection = entity.actions['next'](skip=3)

# You can seed an action with the properties of some other entity

new_entity_action = entity.actions['new-entity']
new_entity_action.populate(entity)
new_entity_action()  # This will call the action with the data set from `entity`
new_entity_action(Name='Another Name')  # This will call the action as above
                                        # but override (or set) the name to be
                                        # 'Another Name'

```

## Config

Configuration can be provided to the `get` function earlier.

```python
import siren_client
entity siren_client.get('http://my_url/', rel_base='https://my_api.com/rels/')
```

 - `rel_base` If set to a value, and this value is at the start of any rel
    that rel will have that value removed:

    Example:
    setting the rel_base to 'http://my.company/schema/' will convert any
    rel from the API (such as 'http://my.company/schema/my_link') to a
    shortened version (in this example: `my_link`)

 - `dumps` Provide your own function for serialising any requests. By default
    Siren Client will inspect the content type and automatically
    serialise into JSON as needed. The function will receive two
    parameters, the requested content type, and the data to serialise.

    ```python
    def my_dumps(content_type, data):
        # Convert data here
        return converted_data
    ```

 - `loads` Provide your own function for de-serialising any requests. By default
    Siren Client will inspect the content type and automatically
    de-serialise from JSON as needed. The function will receive two
    parameters, the requested content type, and the content to
    de-serialise.

    ```python
    def my_loads(content_type, data):
        # Convert data here
        return converted_data
    ```

 - `self_rel` By default the Siren Client will calculate the canonical 'URI' of
    an entity from the link containing a rel called `self`. This
    parameter lets you change the rel that the library will use to
    determine the canonical 'URI'.


## Authentication Setup

The library expects a *requests* session (or similar) to manage the connection
to the server. Whatever methods of authentication requests supports, the
siren-client also supports. Any other transport configuration required (such as
keep-alive, headers etc) can be utilised by configuring the Session or
sub-classing the Session.

### Example Basic Authentication

```python
import siren_client
from requests import Session
from requests.auth import HTTPBasicAuth

session = Session()
session.auth = HTTPBasicAuth('my_username', 'my_password')
entity = siren_client.get('http://my.url.com/', session=session)
```

### Example Session Hook

```python
def mutate_response_somehow(req, *args, **kwargs):
    # do something
    print r.url

session = Session()
session.hooks['response'] = mutate_response_somehow
entity = siren_client.get('http://my.url.com/', session=session)
```

### Example Custom Header

```python
session = Session()
session.headers['X-Pizza'] = 'pepperoni'
entity = siren_client.get('http://my.url.com/', session=session)
```

### Other plugins for Requests Session

 - https://github.com/requests/requests-oauthlib

## Replace Requests Session with your own transport

The session simply provides a transport mechanism for the client. It could be
completely replaced with an arbitrary object doing arbitrary things (such as
communicating in some way other than HTTP). The only methods that are called on
the Session object are the HTTP verbs, with the `get` being used for following
links, etc. If your siren API provided a method of 'hyperspace' in an action
definition, then the library would attempt to call the `hyperspace` method on
the session transport.

Regardless of which method is used to get the data from the server, the response
is then required to have two attributes and one method:

  - `content` This can be whatever you want. By default it attempt to be
    de-serialized as JSON
  - `headers` A dictionary
  - `raise_for_status()` This allows the response to throw an exception if there
    is something wrong.


## Maintainers

Lonely Planet maintains this code as a library that it actively uses.
Contributions are welcome in the form of bug reports and pull requests.

