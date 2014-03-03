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
* Creation syntax for the Client: allow use of .netrc file or explicit credentials. Only required arguments are scheme and host.

    - Use default .netrc file location ($HOME):

      Client(scheme='http', host='localhost', port='8080', context='nuxeo')

    - Use explicit .netrc file location:

      Client(scheme='http', host='localhost', port='8080', context='nuxeo', netrc_file='/path/to/netrc/file')

    - Use explicit credentials:

      Client(scheme='http', host='localhost', port='8080', context='nuxeo', login='Administrator', password='Administrator')

* json.dumps uses sorted dictionary of parameters.

