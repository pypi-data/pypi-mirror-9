__version__ = '1.0.1'


from .client import SirenClient


def get(url, **kwargs):
    if 'session' not in kwargs:
        from requests import Session
        session = Session()
    else:
        session = kwargs.pop('session')
    siren = SirenClient(session=session, config=kwargs)
    return siren.follow(url)
