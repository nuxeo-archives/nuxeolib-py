from session import Session


class Client(object):
    def __init__(self, root, login, password):
        self.root = root
        self.login = login
        self.password = password
        self.session = None

    def getSession(self):
        """"Returns a low-level session to the server.
        """
        if not self.session:
            self.session = Session(self.root, self.login, self.password)
        return self.session

    def getRoot(self):
        """Returns the root folder as a Document object.
        """
        return self.getDocument("/")

    def getDocument(self, path):
        """Get document for path.
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
        self.dirty = {}

    def __getitem__(self, key):
        if self.properties.has_key(key):
            return self.properties[key]
        else:
            return getattr(self, key)

    def __setitem__(self, key, value):
        self.properties[key] = value
        self.dirty[key] = value

    def refresh(self):
        """Refreshes own properties.
        """
        dict = self.session.fetch(self.path)
        self._update(dict)

    def save(self):
        dict = self.session.update(self.path, self.dirty)
        self._update(dict)

    def getBlob(self):
        """Returns the blob for this document.
        """
        if self.type == "Note":
            # Hack
            return self["note:note"]
        else:
            return self.session.getBlob(self.path)

    def setBlob(self, blob):
        """Sets the blob for this document.
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
        child_doc = self.session.create(self.path, type, name)
        return Document(self.session, child_doc)

    def delete(self):
        self.session.delete(self.path)
