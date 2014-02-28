About
-----

This module features a small Python client for the Nuxeo Document Automation
JSON-RPC API.

Prerequisites
-------------

This module has been tested using Python 2.6 and doesn't currently work with
any previous versions.

Install
-------

Run "python setup.py install".

New features
------------

* Support of .netrc hidden password
* Support of CRUD REST API
* Support of USER category based on CRUD REST API

Modifications
-------------
* Creation syntax for the Client:
Client (host = "localhost:8080")
* Username/password obtained from .netrc file
* json.dumps uses sorted dictionary of parameters.

