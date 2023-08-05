# python 3 has different package names
try: from cStringIO import StringIO
except ImportError: from io import StringIO

import json
import functools
from tornado.httpclient import HTTPRequest, HTTPResponse

from .collection import RequestCollection

class stub(object):

    def __init__(self, url, *args, **kwargs):
        self.request = HTTPRequest(url, *args, **kwargs)

    def and_return(self, code=200, body=None, body_json=None):
        """ When we get the response details in this call, we'll partially
        apply the HTTPResponse constructor, leaving out the status code and
        request object.  Those we'll fill in when fetching from the collection,
        just before returning to the user
        """
        if not body and body_json:
            body = json.dumps(body_json)
        if not body:
            body = ''
        self.response_partial = functools.partial(HTTPResponse,
                code=code, buffer=StringIO(body))
        RequestCollection.add(self.request, self.response_partial)
        return self

    def __enter__(self):
        pass

    def __exit__(self, *args, **kwargs):
        RequestCollection.remove(self.request)

def reset():
    RequestCollection.reset()
