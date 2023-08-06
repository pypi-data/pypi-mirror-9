# -*- coding: utf-8 -*-

"""
erequests
~~~~~~~~~

This module contains an asynchronous replica of ``requests.api``, powered
by eventlet.
"""

__version__ = '0.4.1'

import eventlet

# Monkey-patch.
requests = eventlet.patcher.import_patched('requests.__init__')

__all__ = ['__version__', 'map', 'imap', 'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request', 'async', 'AsyncRequest']

# Export same items as vanilla requests
__requests_imports__ = ['utils', 'session', 'Session', 'codes', 'RequestException', 'Timeout', 'URLRequired', 'TooManyRedirects', 'HTTPError', 'ConnectionError']
eventlet.patcher.slurp_properties(requests, globals(), srckeys=__requests_imports__)
__all__.extend(__requests_imports__)
del requests, __requests_imports__


class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response. Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, session=None):
        self.method = method
        self.url = url
        self.session = session or Session()
        self._prepared_kwargs = None

    def prepare(self, **kwargs):
        assert self._prepared_kwargs is None, 'cannot call prepare multiple times'
        self._prepared_kwargs = kwargs

    def send(self, **kwargs):
        kw = self._prepared_kwargs or {}
        kw.update(kwargs)
        return self.session.request(self.method, self.url, **kw)

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.method)


class AsyncRequestFactory(object):
    """ Factory for AsyncRequests. Serious business yo!
    """

    request_cls = AsyncRequest


    @classmethod
    def request(cls, method, url, **kwargs):
        session = kwargs.pop('session', None)
        r = cls.request_cls(method, url, session)
        r.prepare(**kwargs)
        return r

    @classmethod
    def get(cls, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return cls.request('GET', url, **kwargs)

    @classmethod
    def options(cls, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return cls.request('OPTIONS', url, **kwargs)

    @classmethod
    def head(cls, url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return cls.request('HEAD', url, **kwargs)

    @classmethod
    def post(cls, url, data=None, **kwargs):
        return cls.request('POST', url, data=data, **kwargs)

    @classmethod
    def put(cls, url, data=None, **kwargs):
        return cls.request('PUT', url, data=data, **kwargs)

    @classmethod
    def patch(cls, url, data=None, **kwargs):
        return cls.request('PATCH', url, data=data, **kwargs)

    @classmethod
    def delete(cls, url, **kwargs):
        return cls.request('DELETE', url, **kwargs)


# alias for the factory
async = AsyncRequestFactory


def request(method, url, **kwargs):
    req = AsyncRequest(method, url)
    return eventlet.spawn(req.send, **kwargs).wait()


def get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('GET', url, **kwargs)


def options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('OPTIONS', url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return request('HEAD', url, **kwargs)


def post(url, data=None, **kwargs):
    return request('POST', url, data=data, **kwargs)


def put(url, data=None, **kwargs):
    return request('PUT', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('PATCH', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)


def map(requests, size=10):
    """Concurrently converts a sequence of AsyncRequest objects to Responses.

    :param requests: a collection of Request objects.
    :param size: Specifies the number of requests to make at a time, defaults to 10.
    """

    def send(req):
        try:
            return req.send()
        except Exception as e:
            return e

    pool = eventlet.GreenPool(size)
    jobs = [pool.spawn(send, r) for r in requests]

    for j in jobs:
        yield j.wait()


def imap(requests, size=10):
    """Concurrently converts a sequence of AsyncRequest objects to Responses.

    :param requests: a generator of Request objects.
    :param size: Specifies the number of requests to make at a time. defaults to 10.
    """

    pool = eventlet.GreenPool(size)

    def send(r):
        try:
            return r.send()
        except Exception as e:
            return e

    for r in pool.imap(send, requests):
        yield r

