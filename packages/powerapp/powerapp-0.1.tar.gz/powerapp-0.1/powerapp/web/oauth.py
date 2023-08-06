# -*- coding: utf-8 -*-
"""
Generic functions to register OAuth 2.0 clients can be implemented like this:

.. code-block:: python

    @register_oauth_client('github')
    def github_client():
        ...

By convention, for the callback client "foo" settings
"FOO_CLIENT_ID" and "FOO_CLIENT_SECRET", required for the OAuth flow have to
be defined.

The callback function will be called from the `oauth2cb`

"""
import datetime
import uuid
import requests
from six.moves.urllib import parse
from bottle import request, response, abort
from powerapp.config import config
from powerapp.models.oauth_tokens import AccessToken
from powerapp.web.utils import extend_qs, get_redirect_url, get_absolute_url


oauth_clients = {}



class register_oauth_client(object):
    """
    Decorator to register new OAuth client.
    """

    def __init__(self, name, authorize_endpoint, access_token_endpoint,
                 scope=None,
                 client_id=None, client_secret=None,
                 callback_class=None,
                 oauth2cb_redirect_uri='/'):
        self.name = name
        self.authorize_endpoint = authorize_endpoint
        self.access_token_endpoint = access_token_endpoint
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_class = callback_class or OAuthClient
        self.oauth2cb_redirect_uri = oauth2cb_redirect_uri

    def __call__(self, fn):
        instance = self.callback_class(self.name, fn,
                                       self.authorize_endpoint,
                                       self.access_token_endpoint,
                                       scope=self.scope,
                                       client_id=self.client_id,
                                       client_secret=self.client_secret,
                                       oauth2cb_redirect_uri=self.oauth2cb_redirect_uri)
        oauth_clients[self.name] = instance
        return fn


def get_client_by_name(name):
    """
    Return OAuth client by name
    """
    try:
        return oauth_clients[name]
    except KeyError:
        raise RuntimeError('OAuth client %r not registered' % name)


def get_client_by_state(state):
    """
    Return OAuth client by state, stored in cookies
    """
    state_dict = dict(parse.parse_qsl(state or ''))
    if 'name' not in state_dict or 'secret' not in state_dict:
        abort(403)

    # TODO: check cookie
    cookie_name = get_oauth_state_cookie_name(state_dict['name'])
    cookie_value = request.cookies.get(cookie_name)
    if not cookie_value:
        abort(403)
    response.delete_cookie(cookie_name)
    if state != cookie_value:
        abort(403)
    return get_client_by_name(state_dict['name'])


def get_oauth_state_cookie_name(name):
    return '%s_oauth_state' % name


class OAuthClient(object):
    """
    Base class for OAuth client. Instances are generated automatically from
    `register_oauth_client` decorator and can be accessed by
    `get_client_by_name` functions
    `oauth2cb_redirect_uri' - redirect url for oauth2cb function
    """

    def __init__(self, name, callback_fn, authorize_endpoint,
                 access_token_endpoint, scope=None, client_id=None,
                 client_secret=None, oauth2cb_redirect_uri='/'):
        self.authorize_endpoint = authorize_endpoint
        self.access_token_endpoint = access_token_endpoint
        self.name = name
        self.callback_fn = callback_fn
        self.scope = scope
        self.client_id = client_id or '%s_CLIENT_ID' % name.upper()
        self.client_secret = client_secret or '%s_CLIENT_SECRET' % name.upper()
        self.oauth2cb_redirect_uri = oauth2cb_redirect_uri

    def get_client_id(self):
        return config.get(self.client_id)

    def get_client_secret(self):
        return config.get(self.client_secret)

    def get_oauth2cb_uri(self):
        return get_absolute_url('/oauth2cb')

    def get_authorize_url(self, **kwargs):
        """
        :param kwargs: extra params for authorize url which will overwrite
                       default params
        """
        qs = {
            'client_id': self.get_client_id(),
            'scope': self.scope or '',
            'state': self.create_state(),
            'redirect_uri': self.get_oauth2cb_uri(),
        }
        qs.update(kwargs)
        return extend_qs(self.authorize_endpoint, **qs)

    def exchange_code_for_token(self, code):
        post_data = {
            'client_id': self.get_client_id(),
            'client_secret': self.get_client_secret(),
            'code': code,
            'redirect_uri': self.get_oauth2cb_uri(),
            'grant_type': 'authorization_code',
        }
        resp = requests.post(self.access_token_endpoint, data=post_data)
        resp.raise_for_status()
        return resp.json()['access_token']

    def save_access_token(self, user, access_token):
        return AccessToken.register(user, self.name, self.scope, access_token)

    def create_state(self):
        """
        Create the state value (as a string), save it to cookie and return it
        as a result of this function.

        We use this state to validate the response
        from the third party and to get to know the callback URL.

        1. Cookie name is "xxxx_oauth_state" (for example, "todoist_oauth_state")
        2. It's value (the same value we pass through the OAuth loop):
           `name=<oauth_client_name>&secret=<random_secret>&redirect=<callback_url>`
           (here redirect is the page where the account has to be redirected on success)
        """
        cookie_name = get_oauth_state_cookie_name(self.name)
        redirect_url = get_redirect_url()
        state = parse.urlencode({'name': self.name,
                                 'secret': uuid.uuid4(),
                                 'redirect': redirect_url})
        response.set_cookie(cookie_name, state, httponly=True, path='/')
        return state

    def get_state(self):
        """
        Return OAuth state value from cookie.
        """
        cookie_name = get_oauth_state_cookie_name(self.name)
        state = request.get_cookie(cookie_name)
        return state

    def parse_state(self, state):
        """
        parse the state argument
        """
        return dict(parse.parse_qsl(state or ''))
