import urllib2, base64, time, os
import httplib
import logging as log
import json
import mimetypes, random
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


class Session(object):
    """Low-level session that mirrors the RESTful API.
    """
    def __init__(self, server, login, passwd):

        self.server = server
        self.root = self.server + "/site/automation/"
        self.api = self.server + "/api/v1/user"

        self.login = login
        self.passwd = passwd
        self.auth = 'Basic %s' % base64.b64encode(
                self.login + ":" + self.passwd).strip()

        cookie_processor = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(cookie_processor)

        self.fetchAPI()

    def fetchAPI(self):
        headers = {
            "Authorization": self.auth,
        }
        req = urllib2.Request(self.root, headers=headers)
        response = json.loads(self.opener.open(req).read())
        self.operations = {}
        for operation in response["operations"]:
            self.operations[operation['id']] = operation

    # Document category

    def create(self, ref, type, name=None, properties=None):
        return self._execute("Document.Create", input="doc:"+ref,
            type=type, name=name, properties=properties)

    def update(self, ref, properties=None):
        return self._execute("Document.Update", input="doc:"+ref,
            properties=properties)

    def setProperty(self, ref, xpath, value):
        return self._execute("Document.SetProperty", input="doc:"+ref,
            xpath=xpath, value=value)

    def delete(self, ref):
        return self._execute("Document.Delete", input="doc:"+ref)

    def getChildren(self, ref):
        return self._execute("Document.GetChildren", input="doc:"+ref)

    def getParent(self, ref):
        return self._execute("Document.GetParent", input="doc:"+ref)

    def lock(self, ref):
        return self._execute("Document.Lock", input="doc:"+ref)

    def unlock(self, ref):
        return self._execute("Document.Unlock", input="doc:"+ref)

    def move(self, ref, target, name=None):
        return self._execute("Document.Move", input="doc:"+ref,
            target=target, name=name)

    def copy(self, ref, target, name=None):
        return self._execute("Document.Copy", input="doc:"+ref,
            target=target, name=name)

    # These ones are special: no 'input' parameter
    def fetch(self, ref):
        return self._execute("Document.Fetch", value=ref)

    def query(self, query, language=None):
        return self._execute("Document.Query", query=query, language=language)

    # Blob category

    def getBlob(self, ref):
        return self._execute("Blob.Get", input="doc:"+ref)

    # Special case. Yuck:(
    def attachBlob(self, ref, blob):
        return self._attach_blob(blob, document=ref)

    # User category
    def read_user(self, name):
        return self._execute_api(param="/" + name)

    def create_user(self, user, firstName, lastName, email, password):
        dp = {}
        dp['username'] = user
        dp['email'] = email
        dp['lastName'] = lastName
        dp['firstName'] = firstName
        dp['password'] = password

        d = {}
        d['entity-type'] = 'user'
        d['id'] = user
        d['properties'] = dp

        data = json.dumps(d, sort_keys=True)
        data = data.strip()

        return self._execute_api(data=data)

    def delete_user(self, user):
        return self._execute_api(method='DELETE', param="/" + user)

    # Private

    def _execute_api(self, method=None, param="", data=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth,
            "X-NXDocumentProperties": "*",
        }

        req = urllib2.Request(self.api + param, data=data, headers=headers)
        # Default method is POST
        if method is not None:
            req.get_method = lambda: method
        try:
            resp = self.opener.open(req)
	    info = resp.info()
	    s = resp.read()
	    if info.has_key('content-type') and \
		   info['content-type'].startswith("application/json"):
		if s:
		    return json.loads(s)
		else:
		    return None
	    else:
		return s

        except urllib2.HTTPError as e:
            if e.code == 404:
                self._handle_error(e, debug=True)
            else:
                self._handle_error(e)
        except Exception as e:
            self._handle_error(e)
            #raise



    def _execute(self, command, input=None, **params):
        self._checkParams(command, input, params)
        headers = {
            "Content-Type": "application/json+nxrequest",
            "Authorization": self.auth,
            "X-NXDocumentProperties": "*",
        }
        d = {}
        if params:
            d['params'] = {}
            for k, v in params.items():
                if v is None:
                    continue
                if k == 'properties':
                    s = ""
                    for propname, propvalue in v.items():
                        s += "%s=%s\n" % (propname, propvalue)
                    d['params'][k] = s.strip()
                else:
                    d['params'][k] = v
        if input:
            d['input'] = input
        if d:
	    # better keep dictionary sorted
            data = json.dumps(d, sort_keys=True)
        else:
            data = None

        req = urllib2.Request(self.root + command, data, headers)
        try:
            resp = self.opener.open(req)
        except Exception, e:
            self._handle_error(e)
            raise

        info = resp.info()
        s = resp.read()
        if info.has_key('content-type') and \
                info['content-type'].startswith("application/json"):
            if s:
                return json.loads(s)
            else:
                return None
        else:
            return s

    def _attach_blob(self, blob, **params):
        ref = params['document']
        filename = os.path.basename(ref)

        container = MIMEMultipart("related",
                type="application/json+nxrequest",
                start="request")

        d = {'params': params}
        json_data = json.dumps(d, sort_keys=True)
        json_part = MIMEBase("application", "json+nxrequest")
        json_part.add_header("Content-ID", "request")
        json_part.set_payload(json_data)
        container.attach(json_part)

        ctype, encoding = mimetypes.guess_type(filename)
        if ctype:
            maintype, subtype = ctype.split('/', 1)
        else:
            maintype, subtype = "application", "binary"
        blob_part = MIMEBase(maintype, subtype)
        blob_part.add_header("Content-ID", "input")
        blob_part.add_header("Content-Transfer-Encoding", "binary")
        blob_part.add_header("Content-Disposition",
            "attachment;filename=%s" % filename)

        blob_part.set_payload(blob)
        container.attach(blob_part)

        # Create data by hand :(
        boundary = "====Part=%s=%s===" % (time.time, random.randint(0, 1000000000))
        headers = {
                "Accept": "application/json+nxentity, */*",
                "Authorization": self.auth,
                "Content-Type": 'multipart/related;boundary="%s";type="application/json+nxrequest";start="request"'
                    % boundary,
        }
        data = "--" + boundary + "\r\n" \
                + json_part.as_string() + "\r\n" \
                + "--" + boundary + "\r\n" \
                + blob_part.as_string() + "\r\n" \
                + "--" + boundary + "--"

        req = urllib2.Request(self.root + "Blob.Attach", data, headers)
        try:
            resp = self.opener.open(req)
        except Exception, e:
            self._handle_error(e)
            raise

        s = resp.read()
        return s

    def _checkParams(self, command, input, params):
        method = self.operations[command]
        required_params = []
        other_params = []
        for param in method['params']:
            if param['required']:
                required_params.append(param['name'])
            else:
                other_params.append(param['name'])
        for param in params.keys():
            if not param in required_params \
                and not param in other_params:
                raise Exception("Bad param: %s" % param)
        for param in required_params:
            if not param in params.keys():
                raise Exception("Missing param: %s" % param)
        # TODO: add typechecking

    def _handle_error(self, e, debug=False):
        if debug:
            log.debug(e)
        else:
            log.error(e)
        if hasattr(e, "fp"):
            detail = e.fp.read()
            try:
                exc = json.loads(detail)
                if debug:
                    log.debug(exc['message'])
                    log.debug(exc['stack'])
                else:
                    log.error(exc['message'])
                    log.error(exc['stack'])
            except:
                # Error message should always be a JSON message, but sometimes it's not
                if debug:
                    log.debug(detail)
                else:
                    log.error(detail)
