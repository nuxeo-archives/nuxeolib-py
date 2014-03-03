#!/usr/bin/env python

from nuxeolib import Client

SCHEME = 'http'
HOST = "localhost"
PORT = '8080'
CONTEXT = 'nuxeo'
NETRC_FILE = 'test/resources/.netrc'


def main():
    client = Client(SCHEME, HOST, port=PORT, context=CONTEXT,
                    netrc_file=NETRC_FILE)
    children = client.getRoot().getChildren()
    print children
    for doc in children:
        print "Deleting:", doc.path
        doc.delete()

if __name__ == '__main__':
    main()
