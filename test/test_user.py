#!/usr/bin/env python

import unittest
from config import *
from nuxeolib import Client


class SimpleTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(SCHEME, HOST, port=PORT, context=CONTEXT,
                             netrc_file=NETRC_FILE)
        self.session = self.client.getSession()
        self.username = 'test_user'

    def testCreateUser(self):

        userinfo = self.session.read_user(self.username)
        if not userinfo:
            self.session.create_user(self.username, "John", "Doe",
                                     "john.doe@company.com", 'secret')
        userinfo = self.session.read_user(self.username)['properties']

        self.assertEquals(userinfo['username'], 'test_user')
        self.assertEquals(userinfo['firstName'], 'John')
        self.assertEquals(userinfo['lastName'], 'Doe')
        self.assertEquals(userinfo['email'], 'john.doe@company.com')

    def tearDown(self):
        self.session.delete_user(self.username)
