alf
===

.. image:: https://travis-ci.org/globocom/alf.svg?branch=master
    :target: https://travis-ci.org/globocom/alf
    
Python OAuth 2 Client
---------------------

`alf` is an OAuth 2 Client based on `requests.Session
<http://docs.python-requests.org/en/latest/user/advanced/#session-objects>`_
with seamless support for the `Client Credentials Flow
<http://tools.ietf.org/html/draft-ietf-oauth-v2-31#section-1.3.4>`_.

Features
--------

* Automatic token retrieving and renewing
* Token expiration control
* Automatic token storage
* Automatic retry on status 401 (UNAUTHORIZED)

Usage
-----

Initialize the client and use it as a `requests.Session
<http://docs.python-requests.org/en/latest/user/advanced/#session-objects>`_
object.

.. code-block:: python

    from alf.client import Client

    alf = Client(
        token_endpoint='http://example.com/token',
        client_id='client-id',
        client_secret='secret')

    resource_uri = 'http://example.com/resource'

    alf.put(
        resource_uri, data='{"name": "alf"}',
        headers={'Content-Type': 'application/json'})

    alf.get(resource_uri)

    alf.delete(resource_uri)

Using your custom token storage
-------------------------------

Now passing an object with get and set attributes you can store or retrieve a token.

This object can be a Redis, Memcache or your custom object.

.. code-block:: python

    from alf.client import Client
    from redis import StrictRedis

    redis = StrictRedis(host='localhost', port=6379, db=0)

    alf = Client(
        token_endpoint='http://example.com/token',
        client_id='client-id',
        client_secret='secret',
        token_storage=redis)

    resource_uri = 'http://example.com/resource'

    alf.put(
        resource_uri, data='{"name": "alf"}',
        headers={'Content-Type': 'application/json'})

    alf.get(resource_uri)

    alf.delete(resource_uri)


How does it work?
-----------------

Before any request the client tries to retrive a token on the endpoint,
expecting a JSON response with the ``access_token`` and ``expires_in`` keys.

The client keeps the token until it is expired, and according to the ``expires_in``
value calculates an ``expires_on`` value to store and validate token from multiple clients.

After getting the token, the request is issued with a `Bearer authorization
header <http://tools.ietf.org/html/draft-ietf-oauth-v2-31#section-7.1>`_:

.. code-block::

    GET /resource/1 HTTP/1.1
    Host: example.com
    Authorization: Bearer token

If the request fails with a 401 (UNAUTHORIZED) status, a new token is retrieved
from the endpoint and the request is retried. This happens only once, if it
fails again the error response is returned.

Workflow
--------

.. image:: assets/workflow.png

Troubleshooting
---------------

In case of an error retrieving a token, the error response will be returned,
the real request won't happen.


Related projects
----------------

`djalf <https://github.com/viniciuschagas/djalf>`_
''''''''''''''''''''''''''''''''''''''''''''''''''

An extended client that uses Django's cache backend to share tokens between
server instances.


`tornado-alf <https://github.com/globocom/tornado-alf>`_
''''''''''''''''''''''''''''''''''''''''''''''''''''''''

A port of the `alf` client using tornado's `AsyncHTTPClient`.
