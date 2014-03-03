from nuxeolib import Client
import unittest, time
from config import *

from pprint import pprint

class ClientTest(unittest.TestCase):

    def setUp(self):
        self.client = Client(SCHEME, HOST, port=PORT, context=CONTEXT,
                             netrc_file=NETRC_FILE)
        self.root = self.client.getRoot()

        testFolderName = "testfolder-%s" % time.time()
        self.testFolder = self.root.create(testFolderName, "Folder")

    def tearDown(self):
        self.testFolder.delete()


    def testCreateFolder(self):
        name = 'toto-%s' % time.time()
        folder = self.testFolder.create(name, "Folder")
        self.assertEqual(name, folder.name)
        self.assertEqual(name, folder['name'])
        self.assertEqual(0, len(folder.getChildren()))
        self.assertEquals(1, len(self.testFolder.getChildren()))

    def testCreateNote(self):
        name = 'toto-%s' % time.time()
        document = self.testFolder.create(name, "Note")
        self.assertEqual(name, document.name)
        self.assertEqual(name, document['name'])

        self.assertEquals(1, len(self.testFolder.getChildren()))

        blob = document.getBlob()
        self.assertEquals(None, blob)

        document.setBlob("toto")
        blob = document.getBlob()
        self.assertEquals("toto", blob)

    def testCreateFile(self):
        self.assertEquals(0, len(self.testFolder.getChildren()))
        name = 'toto-%s' % time.time()
        document = self.testFolder.create(name, "File")
        self.assertEqual(name, document.name)

        self.assertEquals(1, len(self.testFolder.getChildren()))

        blob = document.getBlob()
        self.assertEquals("", blob)

        document.setBlob("toto")
        blob = document.getBlob()
        self.assertEquals("toto", blob)

    def testDelete(self):
        name = 'toto-%s' % time.time()
        folder = self.testFolder.create(name, "Folder")
        folder.delete()

    def testDeleteTree(self):
        name = 'toto-%s' % time.time()
        folder = self.testFolder.create(name, "Folder")

        name = 'toto-%s' % time.time()
        folder1 = folder.create(name, "Folder")

        folder.delete()

    def testEditProperty(self):
        self.testFolder['dc:title'] = "Some new title"
        self.testFolder.save()
        self.assertEqual("Some new title", self.testFolder['dc:title'])
        self.assertEqual("Some new title", self.testFolder.title)