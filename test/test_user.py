#!/usr/bin/env python

import random
import unittest
import sys
from config import *
from nuxeolib import Client


if __name__ == '__main__':

    user = sys.argv[1]

    host = "localhost:8081"

    client = Client(host)
    session = client.getSession()
    
    userinfo = session.read_user (user)
    if not userinfo:
	session.create_user (user, "a", user, "%s@a.b" % user, user)
	userinfo = session.read_user (user)

    print userinfo
