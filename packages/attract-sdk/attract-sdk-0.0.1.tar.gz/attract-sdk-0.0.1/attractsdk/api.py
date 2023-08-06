import base64
import requests
import json
import logging
import platform
import sys

import attractsdk.utils as utils
from attractsdk import exceptions
from attractsdk.config import __version__


class Api(object):

    # User-Agent for HTTP request
    library_details = "requests {0}; python {1}".format(
        requests.__version__, platform.python_version())
    user_agent = "Attract-Python-SDK/{0} ({1})".format(
        __version__, library_details)
    _api_singleton = None
    def __init__(self, options=None, **kwargs):
        """Create API object

        Usage::

            >>> from attractsdk import Api
            >>> Api.Default(
                    endpoint="http://localhost:5000",
                    username='USERNAME',
                    password='PASSWORD'
                )
        """
        kwargs = utils.merge_dict(options or {}, kwargs)

        self.endpoint = kwargs["endpoint"]
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.token = kwargs["token"] if kwargs.get("token") else None
        self.options = kwargs

    @staticmethod
    def Default(**kwargs):
        """Initialize the API in a singleton style
        """
        if Api._api_singleton is None:
            try:
                Api._api_singleton = Api(
                    endpoint=kwargs["endpoint"],
                    username=kwargs["username"],
                    password=kwargs["password"])
            except KeyError:
                #raise exceptions.MissingConfig("Missing configuration value")
                print("Missing configuration value. Initialize with Api.Default().")
                sys.exit(0)

        return Api._api_singleton


    def basic_auth(self, token=None):
        """Returns base64 encoded token. Used to encode credentials
        for retrieving the token.
        """
        if token:
            credentials = "{0}:0".format(token['token'])
        else:
            credentials = "%s:%s" % (self.username, self.password)
        return base64.b64encode(credentials.encode('utf-8')).decode('utf-8').replace("\n", "")

    def get_token(self):
        """Generate new token by making a POST request
        """
        path = "/tokens"
        payload = {'username': self.username}

        if self.token:
            return self.token
        else:
            # If token is not set we do initial request with username and password
            self.token = self.http_call(
                utils.join_url(self.endpoint, path), "POST",
                data=payload,
                headers={
                    "Authorization": ("Basic {0}".format(self.basic_auth())),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": self.user_agent
                })

            return self.token

    def request(self, url, method, body=None, headers=None):
        """Make HTTP call, formats response and does error handling.
        Uses http_call method in API class.
        """

        http_headers = utils.merge_dict(self.headers(), headers or {})

        if http_headers.get('Attract-Request-Id'):
            logging.info("Attract-Request-Id: {0}".format(http_headers['Attract-Request-Id']))

        try:
            return self.http_call(url, method, data=json.dumps(body), headers=http_headers)

        except exceptions.BadRequest as error:
            return {"error": json.loads(error.content)}

        # Handle unauthorized token
        except exceptions.UnauthorizedAccess as error:
            raise error

    def http_call(self, url, method, **kwargs):
        """Makes a http call. Logs response information.
        """
        # logging.info("Request[{0}]: {1}".format(method, url))
        response = requests.request(method, url, **kwargs)
        # logging.info("Response[{0}]: {1}".format(response.status_code, response.reason))
        return self.handle_response(response, response.content.decode('utf-8'))

    def handle_response(self, response, content):
        """Check HTTP response codes
        """
        status = response.status_code
        if status in (301, 302, 303, 307):
            raise exceptions.Redirection(response, content)
        elif 200 <= status <= 299:
            return json.loads(content) if content else {}
        elif status == 400:
            raise exceptions.BadRequest(response, content)
        elif status == 401:
            raise exceptions.UnauthorizedAccess(response, content)
        elif status == 403:
            raise exceptions.ForbiddenAccess(response, content)
        elif status == 404:
            raise exceptions.ResourceNotFound(response, content)
        elif status == 405:
            raise exceptions.MethodNotAllowed(response, content)
        elif status == 409:
            raise exceptions.ResourceConflict(response, content)
        elif status == 410:
            raise exceptions.ResourceGone(response, content)
        elif status == 422:
            raise exceptions.ResourceInvalid(response, content)
        elif 401 <= status <= 499:
            raise exceptions.ClientError(response, content)
        elif 500 <= status <= 599:
            raise exceptions.ServerError(response, content)
        else:
            raise exceptions.ConnectionError(response,
                content, "Unknown response code: #{response.code}")

    def headers(self):
        """Default HTTP headers
        """
        token = self.get_token()

        return {
            "Authorization": ("Basic %s" % self.basic_auth(token=token)),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent
        }

    def get(self, action, headers=None):
        """Make GET request
        """
        return self.request(utils.join_url(self.endpoint, action), 'GET',
            headers=headers or {})

    def post(self, action, params=None, headers=None):
        """Make POST request
        """
        return self.request(utils.join_url(self.endpoint, action), 'POST',
            body=params or {}, headers=headers or {})

    def put(self, action, params=None, headers=None):
        """Make PUT request
        """
        return self.request(utils.join_url(self.endpoint, action), 'PUT',
            body=params or {}, headers=headers or {})

    def patch(self, action, params=None, headers=None):
        """Make PATCH request
        """
        return self.request(utils.join_url(self.endpoint, action), 'PATCH',
            body=params or {}, headers=headers or {})

    def delete(self, action, headers=None):
        """Make DELETE request
        """
        return self.request(utils.join_url(self.endpoint, action), 'DELETE',
            headers=headers or {})
