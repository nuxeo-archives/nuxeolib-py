#!/usr/bin/env python

import random
import unittest
from config import *
from nuxeolib import Client

class SimpleTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(SCHEME, HOST, port=PORT, context=CONTEXT,
                             netrc_file=NETRC_FILE)
        self.session = self.client.getSession()
        self.doc_name = "doc%s" % random.randint(0, 1000000000)

    def testCreateFile(self):
        self._testCreate("File")

    def testCreateFolder(self):
        self._testCreate("Folder")

    def testCreateWorkspace(self):
        self._testCreate("Workspace")

    def _testCreate(self, type):
        self.session.create("/", type, self.doc_name)

        doc = self.session.fetch("/" + self.doc_name)
        self.assertEquals(type, doc['type'])
        self.assertEquals(self.doc_name, doc['title'])
        self.assertEquals("/"+self.doc_name, doc['path'])

        result = self.session.getChildren("/")
        docs = [ doc for doc in result['entries'] if doc['title'] == self.doc_name ]
        self.assertEquals(1, len(docs))

        doc = self.session.getParent("/" + self.doc_name)
        self.assertEquals("/", doc['path'])

        self.session.delete("/" + self.doc_name)

    def testUsingUuid(self):
        doc = self.session.create("/", "File", self.doc_name)
        uuid = doc['uid']
        doc = self.session.fetch(uuid)
        self.session.delete("/" + self.doc_name)

class SingleFileTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(SCHEME, HOST, port=PORT, context=CONTEXT,
                             netrc_file=NETRC_FILE)
        self.session = self.client.getSession()
        self.doc_name = "doc%s" % random.randint(0, 1000000000)
        self.session.create("/", "File", self.doc_name)

    def tearDown(self):
        try:
            self.session.delete("/" + self.doc_name)
        except:
            pass

    def testGetBlob(self):
        blob = self.session.getBlob("/" + self.doc_name)
        self.assertEquals('', blob)

    def testAttachBlob(self):
        self.session.attachBlob("/" + self.doc_name, "new blob")
        blob = self.session.getBlob("/" + self.doc_name)
        self.assertEquals('new blob', blob)

    def testSetProperty(self):
        self.session.setProperty("/" + self.doc_name, 'dc:title', 'new title')
        doc = self.session.fetch("/" + self.doc_name)
        self.assertEquals('new title', doc['title'])

    def testUpdate(self):
        self.session.update("/" + self.doc_name, {'dc:title': 'new title'})
        doc = self.session.fetch("/" + self.doc_name)
        self.assertEquals('new title', doc['title'])

    def testSimpleQuery(self):
        query = "SELECT * FROM File"
        result = self.session.query(query)
        docs = [ doc for doc in result['entries'] if doc['title'] == self.doc_name ]
        self.assertEquals(1, len(docs))

    def testLock(self):
        self.session.lock("/" + self.doc_name)
        self.session.unlock("/" + self.doc_name)


class MultipleFoldersTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(SCHEME, HOST, port=PORT, context=CONTEXT,
                             netrc_file=NETRC_FILE)
        self.session = self.client.getSession()

        self.folder1 = "folder%s" % random.randint(0, 1000000000)
        self.session.create("/", "Folder", self.folder1)

        self.folder2 = "folder%s" % random.randint(0, 1000000000)
        self.session.create("/", "Folder", self.folder2)

        self.file = "file%s" % random.randint(0, 1000000000)
        self.session.create("/" + self.folder1, "File", self.file)

    def tearDown(self):
        try:
            self.session.delete("/" + self.folder1)
        except:
            pass
        try:
            self.session.delete("/" + self.folder2)
        except:
            pass

    def testMove(self):
        self.session.move("/" + self.folder1 + "/" + self.file, "/" + self.folder2)
        doc = self.session.fetch("/" + self.folder2 + "/" + self.file)
        self.assertEquals(self.file, doc['title'])

        # Original has disappeared from source folder
        result = self.session.getChildren("/" + self.folder1)
        docs = [ doc for doc in result['entries'] if doc['title'] == self.file ]
        self.assertEquals(0, len(docs))

    def testCopy(self):
        self.session.copy("/" + self.folder1 + "/" + self.file, "/" + self.folder2)
        doc = self.session.fetch("/" + self.folder2 + "/" + self.file)
        self.assertEquals(self.file, doc['title'])

        # Original is still in the source folder
        doc = self.session.fetch("/" + self.folder1 + "/" + self.file)
        self.assertEquals(self.file, doc['title'])


if __name__ == '__main__':
    unittest.main()

