from __future__ import absolute_import, division, print_function, with_statement

import base64
import binascii
import functools
import hashlib
import hmac
import time
import uuid

from tornado.concurrent import TracebackFuture, chain_future, return_future
from tornado import gen
from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat
from tornado.log import gen_log
from tornado.stack_context import ExceptionStackContext
from tornado.util import u, unicode_type, ArgReplacer

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    import urllib.parse as urllib_parse  # py3
except ImportError:
    import urllib as urllib_parse  # py2

try:
    long  # py2
except NameError:
    long = int  # py3

from tornado.auth import OAuth2Mixin, AuthError, _auth_return_future


class GithubOAuth2Mixin(OAuth2Mixin):
    """Github authentication using OAuth2.

    In order to use, register your application with Github and copy the
    relevant parameters to your application settings.

    * Go to the Github Dev Console at http://console.developers.github.com
    * Select a project, or create a new one.
    * In the sidebar on the left, select APIs & Auth.
    * In the list of APIs, find the Github+ API service and set it to ON.
    * In the sidebar on the left, select Credentials.
    * In the OAuth section of the page, select Create New Client ID.
    * Set the Redirect URI to point to your auth handler
    * Copy the "Client secret" and "Client ID" to the application settings as
      {"github_oauth": {"key": CLIENT_ID, "secret": CLIENT_SECRET}}

    .. versionadded:: 3.2
    """
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _OAUTH_NO_CALLBACKS = False
    _OAUTH_SETTINGS_KEY = 'github_oauth'

    @_auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        """Handles the login for the Github user, returning a user object.

        Example usage::

            class GithubOAuth2LoginHandler(tornado.web.RequestHandler,
                                           tornado.auth.GithubOAuth2Mixin):
                @tornado.gen.coroutine
                def get(self):
                    if self.get_argument('code', False):
                        user = yield self.get_authenticated_user(
                            redirect_uri='http://your.site.com/auth/github',
                            code=self.get_argument('code'))
                        # Save the user with e.g. set_secure_cookie
                    else:
                        yield self.authorize_redirect(
                            redirect_uri='http://your.site.com/auth/github',
                            client_id=self.settings['github_oauth']['key'],
                            scope=['profile', 'email'],
                            response_type='code',
                            extra_params={'approval_prompt': 'auto'})
        """
        http = self.get_auth_http_client()

        body = urllib_parse.urlencode({
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": self.settings[self._OAUTH_SETTINGS_KEY]['key'],
            "client_secret": self.settings[self._OAUTH_SETTINGS_KEY]['secret'],
            # "grant_type": "authorization_code",
        })

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                   functools.partial(self._on_access_token, callback),
                   method="POST", headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}, body=body)

    def _on_access_token(self, future, response):
        """Callback function for the exchange to the access token."""
        try:
            args = escape.json_decode(response.body)
        except:
            future.set_exception(AuthError('Github auth error: %s' % str(response)))
            return

        future.set_result(args)

    def get_auth_http_client(self):
        """Returns the `.AsyncHTTPClient` instance to be used for auth requests.

        May be overridden by subclasses to use an HTTP client other than
        the default.
        """
        return httpclient.AsyncHTTPClient()


class PupilsOAuth2Mixin(OAuth2Mixin):
    """Pupils authentication using OAuth2.

    In order to use, register your application with Github and copy the
    relevant parameters to your application settings.

    * Go to the Github Dev Console at http://console.developers.github.com
    * Select a project, or create a new one.
    * In the sidebar on the left, select APIs & Auth.
    * In the list of APIs, find the Github+ API service and set it to ON.
    * In the sidebar on the left, select Credentials.
    * In the OAuth section of the page, select Create New Client ID.
    * Set the Redirect URI to point to your auth handler
    * Copy the "Client secret" and "Client ID" to the application settings as
      {"github_oauth": {"key": CLIENT_ID, "secret": CLIENT_SECRET}}

    .. versionadded:: 3.2
    """

    _OAUTH_ACCESS_TOKEN_URL = "http://www.gaotech.in/services/oauth/access_token?"
    _OAUTH_AUTHORIZE_URL = "http://www.gaotech.in/services/oauth/ask?"
    _OAUTH_NO_CALLBACKS = False
    _OAUTH_SETTINGS_KEY = 'pupils_oauth'

    @_auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        """Handles the login for the Github user, returning a user object.

        Example usage::

            class PupilsOAuth2LoginHandler(tornado.web.RequestHandler,
                                           tornado.auth.PupilsOAuth2Mixin):
                @tornado.gen.coroutine
                def get(self):
                    if self.get_argument('code', False):
                        user = yield self.get_authenticated_user(
                            redirect_uri='http://your.site.com/auth/github',
                            code=self.get_argument('code'))
                        # Save the user with e.g. set_secure_cookie
                    else:
                        yield self.authorize_redirect(
                            redirect_uri='http://your.site.com/auth/github',
                            client_id=self.settings['pupils_oauth']['key'],
                            scope=['profile', 'email'],
                            response_type='code',
                            extra_params={'approval_prompt': 'auto'})
        """
        http = self.get_auth_http_client()

        body = urllib_parse.urlencode({
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": self.settings[self._OAUTH_SETTINGS_KEY]['key'],
            "client_secret": self.settings[self._OAUTH_SETTINGS_KEY]['secret'],
            # "grant_type": "authorization_code",
            "response_type": "token",
        })

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                   functools.partial(self._on_access_token, callback),
                   method="POST", headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}, body=body)

    def _on_access_token(self, future, response):
        """Callback function for the exchange to the access token."""
        try:
            args = escape.json_decode(response.body)
        except:
            future.set_exception(AuthError('Pupils auth error: %s' % str(response)))
            return

        future.set_result(args)

    def get_auth_http_client(self):
        """Returns the `.AsyncHTTPClient` instance to be used for auth requests.

        May be overridden by subclasses to use an HTTP client other than
        the default.
        """
        return httpclient.AsyncHTTPClient()

