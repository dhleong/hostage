#
# HTTP
#

from os.path import getsize
from urllib import urlencode
import urllib2
import json as JSON

from ..core import Evaluator


def validated_data(fn):
    """Decorate a method that takes data"""
    def wrapped(self, url, params=None, body=None, headers=None, json=None):
        hasParams = params is not None
        hasJson = json is not None
        hasBody = body is not None

        if not (hasBody or hasParams or hasJson):
            raise Exception("You must provide one of params, json, or body")

        elif hasParams and hasJson:
            raise Exception("You cannot provide BOTH params AND json!")

        elif hasJson:
            # format it
            json = JSON.dumps(json)

        return fn(self, url, params, body, headers, json)

    return wrapped


class HttpResult(object):

    """Simple API Result wrapper for Http"""

    def __init__(self, requestResult, error=None):
        """Wrap the result of an HTTP request

        :requestResult: the result instance

        """
        self._requestResult = requestResult
        self._error = error

    def get_status(self):
        """
        :returns: The result code

        """
        if self._requestResult:
            return self._requestResult.getcode()

        else:
            return self._error.code

    def get_reason(self):
        """
        :returns: The status reason

        """
        if self._requestResult:
            return self._requestResult.getcode()  # umm...

        else:
            return self._error.reason

    def get_response(self):
        return self._requestResult

    def json(self):
        """Get the json response
        :returns: a dict of the JSON response,
            or None if the API call failed

        """
        if self._requestResult:
            return JSON.loads(self._requestResult.read())

        return None

    def __str__(self):
        if not self._error:
            return object.__str__(self)

        status = "%d %s" % (self.get_status(), self.get_reason())
        return status + self._error.read()


class Http(Evaluator):

    def __init__(self):
        self._opener = urllib2.build_opener(urllib2.HTTPSHandler)

    def get(self, url):
        """GET the URL.

        :url: The URL fragment to fetch
        :returns: a HttpResult instance

        """
        return self._request("GET", url)

    @validated_data
    def post(self, url, params=None, body=None, headers=None, json=None):
        """POST some data to the URL. Use the kwargs
        params or json for whichever kind of data you
        need to send, but providing both, or not
        providing either, will raise an Exception

        :params: A dict of params to be url-encoded
        :json: A dict or array to be json-encoded
        :returns: A HttpResult

        """

        data = json or body
        return self._request("POST", url, params, data, headers=headers)

    @validated_data
    def put(self, url, params=None, body=None, headers=None, json=None):
        """PUT some data to the URL. Use the kwars
        params or json for whichever kind of data you
        need to send, but providing both, or not
        providing either, will raise an Exception

        :params: A dict of params to be url-encoded
        :json: A dict or array to be json-encoded
        :returns: A HttpResult

        """
        return self._request("PUT", url, params, json)

    def json(self, url):
        """Shortcut to GET the json at URL.

        :url: The URL fragment to fetch
        :returns: a HttpResult instance

        """
        return self.get(url).json()

    def _request(self, method, url, params=None, body=None, headers=None):
        """Prepare a request, optionally with params or body.
        Throws an HTTPError on error

        :method: GET/POST/PUT
        :url: Full url
        :params: Optional, dict of params
        :body: Optional, raw string/binary body
        :returns: a HttpResult

        """

        if params is not None:
            data = urlencode(params)
        elif body is not None:
            data = body
        else:
            data = None

        if method == 'POST' and body:
            if type(body) == file:
                headers['Content-Length'] = getsize(body.name)
            else:
                headers['Content-Length'] = len(data)

        req = urllib2.Request(url, data, headers)
        req.get_method = lambda: method  # hax to support PUT
        try:
            return HttpResult(self._opener.open(req))
        except urllib2.HTTPError, e:
            raise e
