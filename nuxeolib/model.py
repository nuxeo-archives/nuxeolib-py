from session import Session

import netrc

class Client(object):
    def __init__(self, host):

	self.host = host

	self.server = "http://%s/nuxeo" % (self.host)

	secrets = netrc.netrc()
	login, username, password = secrets.authenticators (self.host.split(':')[0])

        self.login = login
        self.password = password
        self.session = None

    def getSession(self):
        """"Returns a low-level session to the server. You probably don't want to use it.
        """
        if not self.session:
            self.session = Session(self.server, self.login, self.password)
        return self.session

    def getRoot(self):
        """Returns the root folder as a Document object.
        """
        return self.getDocument("/")

    def getDocument(self, path):
        """Returns document at the given path.
        """
        session = self.getSession()
        resp = session.fetch(path)
        return Document(session, resp)


class Document(object):
    def __init__(self, session, dict):
        self.session = session
        self._update(dict)

    def _update(self, dict):
        self.type = dict['type']
        self.uid = dict['uid']
        self.path = dict['path']
        self.title = dict['title']
        self.name = self.path.split("/")[-1]
        self.properties = dict.get('properties', {})
        self.dirty_properties = {}

    def __getitem__(self, key):
        """Gets a property value using <schema>:<name> as a key.
        """
        if self.properties.has_key(key):
            return self.properties[key]
        else:
            return getattr(self, key)

    def __setitem__(self, key, value):
        """Sets a property value using <schema>:<name> as a key. Marks it dirty so it can be saved
        by calling 'save()' (don't forget to do it).
        """
        self.properties[key] = value
        self.dirty_properties[key] = value

    def refresh(self):
        """Refreshes own properties.
        """
        dict = self.session.fetch(self.path)
        self._update(dict)

    def save(self):
        """Updates dirty (modified) properties.
        """
        if self.dirty_properties:
            dict = self.session.update(self.path, self.dirty_properties)
            self._update(dict)

    def getBlob(self):
        """Returns the blob (aka content stream) for this document.
        """
        if self.type == "Note":
            # Hack
            return self["note:note"]
        else:
            return self.session.getBlob(self.path)

    def setBlob(self, blob):
        """Sets the blob (aka content stream) for this document.
        """
        if self.type == "Note":
            # Hack
            dict = self.session.setProperty(self.path, "note:note", blob)
            self._update(dict)
        else:
            return self.session.attachBlob(self.path, blob)

    def getChildren(self):
        """Returns children of document as a document.
        """
        dicts = self.session.getChildren(self.path)['entries']
        return [ Document(self.session, dict) for dict in dicts ]

    def create(self, name, type):
        """Creates a new document (or folder) object as child of this document.
        """
        child_doc = self.session.create(self.path, type, name)
        return Document(self.session, child_doc)

    def delete(self):
        """Deletes this document (including children).
        """
        self.session.delete(self.path)
