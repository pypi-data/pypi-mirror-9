#
# Copyright (C) 2014 Conjur Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import base64

import requests

from conjur.variable import Variable
from conjur.user import User
from conjur import ConjurException
from conjur.role import Role
from conjur.group import Group
from conjur.layer import Layer
from conjur.host import Host
from conjur.resource import Resource
from conjur.util import urlescape


class API(object):
    def __init__(self, credentials=None, token=None, config=None):
        """
        Creates an API instance configured with the given credentials or token
        and config.

        Generally you should use `conjur.new_from_key`, `conjur.new_from_netrc`, or `conjur.new_from_token` to
        get an API instance instead of calling this constructor directly.
        """
        if credentials:
            self.login, self.api_key = credentials
            self.token = None
        elif token:
            self.token = token
            self.login = self.api_key = None
        else:
            raise TypeError("must be given a credentials or token argument")
        if config:
            self.config = config
        else:
            import conjur.config

            self.config = conjur.config.config

    def authenticate(self, cached=True):
        """
        Authenticate with Conjur and return a token (str) that can be used
        to establish identity to Conjur services.

        Returns the (json formatted) signed Conjur authentication Token.

        It is an error to call this method if the API was created with a token rather
        than a login and api key.

        :param cached: When True, a cached token value will be used if it is available,
            otherwise the token will be fetched whether or not a cached value is present.
        """
        if cached and self.token:
            return self.token

        if not self.login or not self.api_key:
            raise ConjurException("API created without credentials can't authenticate")

        url = "%s/users/%s/authenticate" % (self.config.authn_url, urlescape(self.login))

        self.token = self._request('post', url, self.api_key).text
        return self.token

    def auth_header(self):
        """
        Get the value of an Authorization header to make Conjur requests, performing
        authentication if necessary.
        """
        token = self.authenticate()
        enc = base64.b64encode(token)
        return 'Token token="%s"' % enc

    def request(self, method, url, **kwargs):
        """
        Make an authenticated request with the given method and url.  Additional arguments are passed
        to requests.<method>.

        Returns a requests.Response object.

        If the response status is not 2xx, raises a ConjurException.

        :param method: One of the standard HTTP verbs (case insensitive).
        :param url: The full url to request.
        :param **kwargs: additional arguments to pass to the requests.<method> call.
        """
        headers = kwargs.setdefault('headers', {})
        headers['Authorization'] = self.auth_header()

        return self._request(method, url, **kwargs)

    def _request(self, method, url, *args, **kwargs):
        if 'verify' not in kwargs:
            if self.config.verify_ssl and self.config.cert_file is not None:
                kwargs['verify'] = self.config.cert_file
            else:
                kwargs['verify'] = self.config.verify_ssl
        check_errors = kwargs.pop('check_errors', True)

        response = getattr(requests, method.lower())(url, *args, **kwargs)
        if check_errors and response.status_code >= 300:
            raise ConjurException("Request failed: %d" % response.status_code)

        return response

    def get(self, url, **kwargs):
        """
        Makes an authenticated GET request to the given :url:.

        Returns a requests.Response object.

        If the response status is not 2xx, raises a ConjurException.

        :param url: the full url to request
        :param **kwargs: same as requests.get options
        """
        return self.request('get', url, **kwargs)

    def post(self, url, **kwargs):
        """
        Makes an authenticated POST request to the given :url:.

        Returns a requests.Response object.

        If the response status is not 2xx, raises a ConjurException.

        :param url: the full url to request
        :param **kwargs: same as requests.post options
        """
        return self.request('post', url, **kwargs)

    def put(self, url, **kwargs):
        """
        Makes an authenticated PUT request to the given :url:.

        Returns a requests.Response object.

        If the response status is not 2xx, raises a ConjurException.

        :param url: the full url to request
        :param **kwargs: same as requests.put options
        """
        return self.request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        """
        Makes an authenticated DELETE request to the given :url:.

        Returns a requests.Response object.

        If the response status is not 2xx, raises a ConjurException.

        :param url: the full url to request
        :param **kwargs: same as requests.delete options
        """
        return self.request('delete', url, **kwargs)

    def role(self, kind, identifier):
        """
        Return a :class `Role <Role>`: object with the given kind and id.

        This method neither creates nor checks for the roles's existence.
        """
        return Role(self, kind, identifier)

    def resource(self, kind, identifier):
        return Resource(self, kind, identifier)

    def group(self, id):
        """
        Return a :class `Group <Group>`: object with the given id.

        This method neither creates nor checks for the groups's existence.
        """
        return Group(self, id)

    def create_group(self, id):
        self.post('{0}/groups'.format(self.config.core_url), data={'id': id})
        return Group(self, id)

    def variable(self, id):
        """
        Return a :class `Variable <Variable>`: object with the given id.

        This method neither creates nor checks for the variable's existence.
        """
        return Variable(self, id)

    def create_variable(self, id=None, mime_type='text/plain', kind='secret', value=None):
        """Creates a Conjur variable.

        Returns a :class `Variable <Variable>`: object

        :param id: An id for the new variable.  If not given, a unique id will be generated.
        :param mime_type: A mime-type indicating the content type stored by the variable.  This
            determines the Content-Type header of responses returning the variables value.
        :param kind: Annotation indicating a user defined kind for the variable.  Ignored by Conjur,
            but useful for making documenting a variable's purpose.
        :param value: An initial value for the variable.
        """
        data = {'mime_type': mime_type, 'kind': kind}
        if id is not None:
            data['id'] = id
        if value is not None:
            data['value'] = value

        attrs = self.post("%s/variables" % self.config.core_url, data=data).json()
        id = id or attrs['id']
        return Variable(self, id, attrs)

    def layer(self, layer_id):
        return Layer(self, layer_id)

    def host(self, host_id):
        return Host(self, host_id)

    def create_host(self, host_id):
        attrs = self.post("{0}/hosts".format(self.config.core_url), data={'id': host_id}).json()
        return Host(self, host_id, attrs)

    def user(self, login):
        """
        Returns an object representing a Conjur user with the given login.

        The user is *not* created by this method, and may in fact not exist.
        """
        return User(self, login)

    def create_user(self, login, password=None):
        """
        Create a Conjur user with the given login.  If password is not given,
        the user will only be able to authenticate using the generated api_key
        attribute of the returned User instance.
        """
        data = {'login': login}
        if password is not None:
            data['password'] = password
        url = "{0}/users".format(self.config.core_url)
        return User(self, login, self.post(url, data=data).json())

    def _public_key_url(self, *args):
        return '/'.join([self.config.pubkeys_url] + [urlescape(arg) for arg in args])

    def add_public_key(self, username, key):
        """
        Upload an openssh formatted key to be made available for the given
        username.
        """
        self.post(self._public_key_url(username), data=key)

    def remove_public_key(self, username, keyname):
        """
        Remove a specific public key for this user.  The keyname
        indicates the name field in the openssh formatted key that was
        uploaded.
        """
        self.delete(self._public_key_url(username, keyname))

    def remove_public_keys(self, username):
        """
        Remove all of username's public keys.
        """
        for keyname in self.public_key_names(username):
            self.remove_public_key(username, keyname)

    def public_keys(self, username):
        """
        Returns all public keys for :username: as a newline separated
        str (because this is the format expected by the authorized-keys-command)
        """
        return self.get(self._public_key_url(username)).text

    def public_key(self, username, keyname):
        """
        Return the contents of a specific public key.  The name of the key
        is based on the name entry of the openssh formatted key that was uploaded.
        """
        return self.get(self._public_key_url(username, keyname)).text

    def public_key_names(self, username):
        """
        Return the names of public keys  for this user.
        """
        return [k.split(' ')[-1] for k in self.public_keys(username).split('\n')]



