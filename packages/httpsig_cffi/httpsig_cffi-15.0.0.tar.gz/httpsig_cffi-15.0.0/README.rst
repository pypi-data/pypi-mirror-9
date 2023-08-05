httpsig_cffi
============

.. image:: https://travis-ci.org/hawkowl/httpsig_cffi.svg?branch=master
    :target: https://travis-ci.org/hawkowl/httpsig_cffi

Sign HTTP requests with secure signatures according to the IETF HTTP Signatures specification (`Draft 3`_).
This is `a fork`_ of the fork_ of the original module_ that was made to fully support both RSA and HMAC schemes as well as unit test both schemes to prove they work.
This particular fork moves from PyCrypto to Cryptography, which provides PyPy support.

See the original project_, original Python module_, original spec_, and `current IETF draft`_ for more details on the signing scheme.

.. _project: https://github.com/joyent/node-http-signature
.. _module: https://github.com/zzsnzmn/py-http-signature
.. _fork: https://github.com/ahknight/httpsig
.. _spec: https://github.com/joyent/node-http-signature/blob/master/http_signing.md
.. _`current IETF draft`: https://datatracker.ietf.org/doc/draft-cavage-http-signatures/
.. _`Draft 3`: http://tools.ietf.org/html/draft-cavage-http-signatures-03
.. _`a fork`: https://github.com/hawkowl/httpsig_cffi


Requirements
------------

* Python 2.7, 3.2, 3.3, 3.4, PyPy, PyPy3
* Cryptography_

Optional:

* requests_

.. _Cryptography: https://pypi.python.org/pypi/cryptography
.. _requests: https://pypi.python.org/pypi/requests


Usage
-----

Real documentation is forthcoming, but for now this should get you started.

For simple raw signing:

.. code:: python

    import httpsig_cffi as httpsig

    secret = open('rsa_private.pem', 'rb').read()

    sig_maker = httpsig.Signer(secret=secret, algorithm='rsa-sha256')
    sig_maker.sign('hello world!')

For general use with web frameworks:

.. code:: python

    import httpsig_cffi as httpsig

    key_id = "Some Key ID"
    secret = b'some big secret'

    hs = httpsig.HeaderSigner(key_id, secret, algorithm="hmac-sha256", headers=['(request-target)', 'host', 'date'])
    signed_headers_dict = hs.sign({"Date": "Tue, 01 Jan 2014 01:01:01 GMT", "Host": "example.com"}, method="GET", path="/api/1/object/1")

For use with requests:

.. code:: python

    import json
    import requests
    from httpsig_cffi.requests_auth import HTTPSignatureAuth

    secret = open('rsa_private.pem', 'rb').read()

    auth = HTTPSignatureAuth(key_id='Test', secret=secret)
    z = requests.get('https://api.example.com/path/to/endpoint',
                             auth=auth, headers={'X-Api-Version': '~6.5'})

Class initialization parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that keys and secrets should be bytes objects.  At attempt will be made to convert them, but if that fails then exceptions will be thrown.

.. code:: python

    httpsig_cffi.Signer(secret, algorithm='rsa-sha256')

``secret``, in the case of an RSA signature, is a string containing private RSA pem. In the case of HMAC, it is a secret password.
``algorithm`` is one of the six allowed signatures: ``rsa-sha1``, ``rsa-sha256``, ``rsa-sha512``, ``hmac-sha1``, ``hmac-sha256``,
``hmac-sha512``.


.. code:: python

    httpsig_cffi.requests_auth.HTTPSignatureAuth(key_id, secret, algorithm='rsa-sha256', headers=None)

``key_id`` is the label by which the server system knows your RSA signature or password.
``headers`` is the list of HTTP headers that are concatenated and used as signing objects. By default it is the specification's minimum, the ``Date`` HTTP header.
``secret`` and ``algorithm`` are as above.


Tests
-----

To run tests::

    tox


License
-------

Both this module and the original module_ are licensed under the MIT license.
