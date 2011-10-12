#!/usr/bin/env python

from nuxeolib import Client

URL = "http://localhost:8080/nuxeo/site/automation/"
LOGIN = 'Administrator'
PASSWD = 'Administrator'

def main():
    client = Client(URL, LOGIN, PASSWD)
    children = client.getRoot().getChildren()
    print children
    for doc in children:
        print "Deleting:", doc.path
        doc.delete()

if __name__ == '__main__':
    main()
