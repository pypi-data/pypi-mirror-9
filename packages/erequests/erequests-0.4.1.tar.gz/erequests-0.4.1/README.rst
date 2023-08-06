ERequests: Asyncronous Requests with Eventlet
=============================================

ERequests allows you to use Requests with Eventlet to make asyncronous HTTP
Requests easily.

ERequests is a port to Eventlet of Kenneth Reitz's grequests (https://github.com/kennethreitz/grequests) though
it doesn't provide the same API these days.


Usage
-----

Usage is simple::

    import erequests

    urls = [
        'http://www.heroku.com',
        'http://tablib.org',
        'http://httpbin.org',
        'http://python-requests.org',
        'http://kennethreitz.com'
    ]

Create a set of unsent Requests::

    >>> rs = (erequests.async.get(u) for u in urls)

Send them all at the same time::

    >>> list(erequests.map(rs))
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>]

NOTE: When sending multiple requests at the same time with map/imap, if any of them results in an error, the exception
object is returned.


Installation
------------

Installation is easy with pip::

    $ pip install erequests

