# coding:utf8

"""
Created on 2014-09-04

@author: tufei
@description:

Copyright (c) 2014 infohold inc. All rights reserved.
"""
import datetime
import base64
import os
import oauthlib.common
from oauthlib.oauth2 import RequestValidator
from dhkit import log


class Client(object):

    def get_id(self):
        """获取OAUTH客户端表示
        :return: string
        """
        raise NotImplementedError

    def validate_secret(self, secret):
        """校验客户端密钥
        :param secret: 密钥
        :return: boolean
        """
        return True

    def get_client_type(self):
        """获取客户端类型，默认为confidential
        :return: string
        """
        return 'confidential'

    def get_response_type(self):
        """获取响应类型，默认为code
        :return: string
        """
        return 'code'

    def get_grant_type(self):
        """获取GrantType，默认为password
        :return: string
        """
        return 'password'

    def get_scopes(self):
        """获取scopes
        :return: list
        """
        return []

    def get_default_scopes(self):
        """默认scopes
        :return: list
        """
        return []

    def get_redirect_uris(self):
        """获取重定向的网址列表
        :return: list
        """
        return []

    def get_default_redirect_uri(self):
        """获取默认的重定向网址
        :return: string
        """
        raise NotImplementedError

    def validate_scopes(self, scopes):
        if isinstance(scopes, (list, tuple)):
            _scopes = scopes
        elif isinstance(scopes, (str, unicode)):
            _scopes = scopes.split(';')
        else:
            raise TypeError("Unkown scopes type")
        return set(self.get_scopes()).issuperset(set(_scopes))


class Grant(object):

    def get_client_id(self):
        raise NotImplementedError

    def get_scopes(self):
        raise NotImplementedError

    def get_user(self):
        raise NotImplementedError

    def get_code(self):
        raise NotImplementedError

    def get_expires_at(self):
        raise NotImplementedError

    def is_expired(self):
        return datetime.datetime.now() > self.get_expires_at()


class Token(object):

    def get_client_id(self):
        raise NotImplementedError

    def get_user(self):
        raise NotImplementedError

    def get_scopes(self):
        raise NotImplementedError

    def get_access_token(self):
        raise NotImplementedError

    def get_expires_at(self):
        raise NotImplementedError

    def is_expired(self):
        return datetime.datetime.now() > self.get_expires_at()

    def validate_scopes(self, scopes):
        if isinstance(scopes, (list, tuple)):
            _scopes = scopes
        elif isinstance(scopes, (str, unicode)):
            _scopes = scopes.split(';')
        else:
            raise TypeError("Unkown scopes type")
        return set(self.get_scopes()).issuperset(set(_scopes))


class OAuthStorage(object):
    
    def get_client(self, client_id):
        """根据OAUTH客户端ID获取Client对象
        :param client_id: 客户端ID
        :return: Client对象
        """
        raise NotImplementedError
    
    def get_grant(self, client_id, code):
        """获取Grant对象
        :param client_id: 客户端ID
        :param code: code
        :return: Grant对象
        """
        raise NotImplementedError

    def save_grant(self, client_id, code, request, *args, **kwargs):
        """ 从request对象中存储Grant对象
        :param request: http request对象
        :param args:
        :param kwargs:
        :return: None
        """
        raise NotImplementedError
    
    def get_token(self, access_token=None, refresh_token=None):
        """获取Token对象
        :param access_token:
        :param refresh_token:
        :return: Token对象
        """
        raise NotImplementedError
    
    def save_token(self, request, token_dict, *args, **kwargs):
        """存储Token对象
        :param request:
        :param token_dict:
        :param args:
        :param kwargs:
        :return: None
        """
        raise NotImplementedError

    def delete_token(self, token):
        """删除Token对象
        :param token:
        :return: None
        """
        raise NotImplementedError

    def auth_user(self, username, password):
        """认证用户
        :param username: 用户名
        :param password: 用户密码
        :return: 用户标示，比如用户ID，或者用户账号等等
        """
        raise NotImplementedError


class OAuth2RequestValidator(RequestValidator):
    
    def __init__(self, oauth_storage):
        self.storage = oauth_storage       

    def client_authentication_required(self, request, *args, **kwargs):
        """Determine if client authentication is required for current request.

        According to the rfc6749, client authentication is required in the following cases:
            - Resource Owner Password Credentials Grant, when Client type is Confidential or when
              Client was issued client credentials or whenever Client provided client
              authentication, see `Section 4.3.2`_.
            - Authorization Code Grant, when Client type is Confidential or when Client was issued
              client credentials or whenever Client provided client authentication,
              see `Section 4.1.3`_.
            - Refresh Token Grant, when Client type is Confidential or when Client was issued
              client credentials or whenever Client provided client authentication, see
              `Section 6`_

        :param request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Resource Owner Password Credentials Grant
            - Refresh Token Grant

        .. _`Section 4.3.2`: http://tools.ietf.org/html/rfc6749#section-4.3.2
        .. _`Section 4.1.3`: http://tools.ietf.org/html/rfc6749#section-4.1.3
        .. _`Section 6`: http://tools.ietf.org/html/rfc6749#section-6
        """
        if request.grant_type == 'password':
            return True
        auth_required = ('authorization_code', 'refresh_token')
        return 'Authorization' in request.headers and request.grant_type in auth_required

    def authenticate_client(self, request, *args, **kwargs):
        """Authenticate client through means outside the OAuth 2 spec.

        Means of authentication is negotiated beforehand and may for example
        be `HTTP Basic Authentication Scheme`_ which utilizes the Authorization
        header.

        Headers may be accesses through request.headers and parameters found in
        both body and query can be obtained by direct attribute access, i.e.
        request.client_id for client_id in the URL query.

        OBS! Certain grant types rely on this authentication, possibly with
        other fallbacks, and for them to recognize this authorization please
        set the client attribute on the request (request.client). Note that
        preferably this client object should have a client_id attribute of
        unicode type (request.client.client_id).

        :param request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Resource Owner Password Credentials Grant (may be disabled)
            - Client Credentials Grant
            - Refresh Token Grant

        .. _`HTTP Basic Authentication Scheme`: http://tools.ietf.org/html/rfc1945#section-11.1
        """
        auth = request.headers.get('Authorization', None)
        if auth:
            try:
                _, s = auth.split(' ')
                client_id, client_secret = base64.b64decode(s).split(':')
                client_id = oauthlib.common.to_unicode(client_id, 'utf-8')
                client_secret = oauthlib.common.to_unicode(client_secret, 'utf-8')
            except Exception, e:
                log.debug('Authenticate client failed with exception: %r', e)
                return False
        else:
            client_id = request.client_id
            client_secret = request.client_secret

        client = self.storage.get_client(client_id)
        if not client:
            log.debug("Authenticate client failed, client not found for client_id:[%s]." % client_id)
            return False

        request.client = client
        if not client.validate_secret(client_secret):
            log.debug("Authenticate client failed, secret not match.")
            return False

        if client.get_client_type() != 'confidential':
            log.debug("Authenticate client failed, not confidential.")
            return False
        log.debug("Authenticate client:[%s] success." % client_id)
        return True

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        """Ensure client_id belong to a non-confidential client.

        A non-confidential client is one that is not required to authenticate
        through other means, such as using HTTP Basic.

        Note, while not strictly necessary it can often be very convenient
        to set request.client to the client object associated with the
        given client_id.

        :param request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
        """
        log.debug("Authenticate client: %s." % client_id)
        client = request.client or self.storage.get_client(client_id)
        if not client:
            log.debug("Authenticate failed, client not found.")
            return False

        if not client.validate_secret(request.client_secret):
            log.debug("Authenticate client failed, secret not match.")
            return False

        # attach client on request for convenience
        request.client = client
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, *args, **kwargs):
        """Ensure client is authorized to redirect to the redirect_uri requested.

        If the client specifies a redirect_uri when obtaining code then
        that redirect URI must be bound to the code and verified equal
        in this method.

        All clients should register the absolute URIs of all URIs they intend
        to redirect to. The registration is outside of the scope of oauthlib.

        :param client_id: Unicode client identifier
        :param code: Unicode authorization_code.
        :param redirect_uri: Unicode absolute URI
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant (during token request)
        """
        client = client or self.storage.get_client(client_id)
        log.debug("Confirm redirect uri for client %r and code %r." % client.client_id, code)
        grant = self.storage.get_grant(client_id, code)
        if not grant:
            log.debug("Grant not found.")
            return False
        if hasattr(grant, 'validate_redirect_uri'):
            return grant.validate_redirect_uri(redirect_uri)
        log.debug("Compare redirect uri for grant %r and %r.", grant.redirect_uri, redirect_uri)

        testing = 'OAUTHLIB_INSECURE_TRANSPORT' in os.environ
        if testing and redirect_uri is None:
            # For testing
            return True

        return grant.redirect_uri == redirect_uri

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        """Get the list of scopes associated with the refresh token.

        :param refresh_token: Unicode refresh token
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: List of scopes.

        Method is used by:
            - Refresh token grant
        """
        log.debug("Obtaining scope of refreshed token.")
        token = self.storage.get_token(refresh_token=refresh_token)
        return token.get_scopes()

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        """Get the default redirect URI for the client.

        :param client_id: Unicode client identifier
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: The default redirect URI for the client

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        request.client = request.client or self.storage.get_client(client_id)
        redirect_uri = request.client.get_default_redirect_uri()
        log.debug("Found default redirect uri %r", redirect_uri)
        return redirect_uri

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        """Get the default scopes for the client.

        :param client_id: Unicode client identifier
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: List of default scopes

        Method is used by all core grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials grant
        """
        request.client = request.client or self.storage.get_client(client_id)
        scopes = request.client.get_default_scopes()
        log.debug("Found default scopes %r", scopes)
        return scopes

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        log.debug("Persist authorization code %r for client %r", code, client_id)
        request.client = request.client or self.storage.get_client(client_id)
        self.storage.save_grant(client_id, code, request, *args, **kwargs)
        return request.client.get_default_redirect_uri()

    def save_bearer_token(self, token, request, *args, **kwargs):
        """Persist the Bearer token.

        The Bearer token should at minimum be associated with:
            - a client and it's client_id, if available
            - a resource owner / user (request.user)
            - authorized scopes (request.scopes)
            - an expiration time
            - a refresh token, if issued

        The Bearer token dict may hold a number of items::

            {
                'token_type': 'Bearer',
                'access_token': 'askfjh234as9sd8',
                'expires_in': 3600,
                'scope': 'string of space separated authorized scopes',
                'refresh_token': '23sdf876234',  # if issued
                'state': 'given_by_client',  # if supplied by client
            }

        Note that while "scope" is a string-separated list of authorized scopes,
        the original list is still available in request.scopes

        :param client_id: Unicode client identifier
        :param token: A Bearer token dict
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: The default redirect URI for the client

        Method is used by all core grant types issuing Bearer tokens:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant (might not associate a client)
            - Client Credentials grant
        """
        log.debug("Save bearer token %r", token)
        self.storage.save_token(request, token, *args, **kwargs)
        return request.client.get_default_redirect_uri()

    def validate_bearer_token(self, token, scopes, request):
        """Ensure the Bearer token is valid and authorized access to scopes.

        :param token: A string of random characters.
        :param scopes: A list of scopes associated with the protected resource.
        :param request: The HTTP Request (oauthlib.common.Request)

        A key to OAuth 2 security and restricting impact of leaked tokens is
        the short expiration time of tokens, *always ensure the token has not
        expired!*.

        Two different approaches to scope validation:

            1) all(scopes). The token must be authorized access to all scopes
                            associated with the resource. For example, the
                            token has access to ``read-only`` and ``images``,
                            thus the client can view images but not upload new.
                            Allows for fine grained access control through
                            combining various scopes.

            2) any(scopes). The token must be authorized access to one of the
                            scopes associated with the resource. For example,
                            token has access to ``read-only-images``.
                            Allows for fine grained, although arguably less
                            convenient, access control.

        A powerful way to use scopes would mimic UNIX ACLs and see a scope
        as a group with certain privileges. For a restful API these might
        map to HTTP verbs instead of read, write and execute.

        Note, the request.user attribute can be set to the resource owner
        associated with this token. Similarly the request.client and
        request.scopes attribute can be set to associated client object
        and authorized scopes. If you then use a decorator such as the
        one provided for django these attributes will be made available
        in all protected views as keyword arguments.

        :param token: Unicode Bearer token
        :param scopes: List of scopes (defined by you)
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is indirectly used by all core Bearer token issuing grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials Grant
        """
        log.debug("Validate bearer token %r", token)
        oauth_token = self.storage.get_token(access_token=token)
        if not oauth_token:
            request.error_message = "Bearer token not found."
            log.debug(request.error_message)
            return False

        # validate expires
        if oauth_token.is_expired():
            request.error_message = "Bearer token is expired."
            log.debug(request.error_message)
            return False

        # validate scopes
        if scopes and not oauth_token.validate_scopes(scopes):
            request.error_message = "Bearer token scope not valid."
            log.debug(request.error_message)
            return False

        request.access_token = oauth_token.get_access_token()
        request.user = oauth_token.get_user()
        request.scopes = scopes
        request.client = self.storage.get_client(oauth_token.get_client_id())
        return True

    def validate_client_id(self, client_id, request, *args, **kwargs):
        """Ensure client_id belong to a valid and active client.

        Note, while not strictly necessary it can often be very convenient
        to set request.client to the client object associated with the
        given client_id.

        :param request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        log.debug("Validate client %r", client_id)
        client = request.client or self.storage.get_client(client_id)
        if client:
            request.client = client  # attach client to request object
            return True
        return False

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        """Ensure the authorization_code is valid and assigned to client.

        OBS! The request.user attribute should be set to the resource owner
        associated with this authorization code. Similarly request.scopes and
        request.state must also be set.

        :param client_id: Unicode client identifier
        :param code: Unicode authorization code
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
        """
        client = client or self.storage.get_client(client_id)
        log.debug("Validate code for client %r and code %r", client.client_id, code)
        grant = self.storage.get_grant(client_id, code)
        if not grant:
            log.debug("Grant not found.")
            return False
        if grant.is_expired():
            log.debug("Grant is expired.")
            return False

        request.state = kwargs.get('state')
        request.user = grant.get_user()
        request.scopes = grant.get_scopes()
        return True

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """Ensure client is authorized to use the grant_type requested.

        :param client_id: Unicode client identifier
        :param grant_type: Unicode grant type, i.e. authorization_code, password.
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials Grant
            - Refresh Token Grant
        """
        # if self._usergetter is None and grant_type == 'password':
        #     log.debug('Password credential authorization is disabled.')
        #     return False

        default_grant_types = (
            'authorization_code', 'password',
            'client_credentials', 'refresh_token',
        )

        if grant_type not in default_grant_types:
            return False

        if hasattr(client, 'allowed_grant_types') and grant_type not in client.allowed_grant_types:
            return False

        # if grant_type == 'client_credentials':
        #     request.user = client.user
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        """Ensure client is authorized to redirect to the redirect_uri requested.

        All clients should register the absolute URIs of all URIs they intend
        to redirect to. The registration is outside of the scope of oauthlib.

        :param client_id: Unicode client identifier
        :param redirect_uri: Unicode absolute URI
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        request.client = request.client or self.storage.get_client(client_id)
        client = request.client
        if hasattr(client, 'validate_redirect_uri'):
            return client.validate_redirect_uri(redirect_uri)
        return redirect_uri in client.redirect_uris

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        """Ensure the Bearer token is valid and authorized access to scopes.

        OBS! The request.user attribute should be set to the resource owner
        associated with this refresh token.

        :param refresh_token: Unicode refresh token
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant (indirectly by issuing refresh tokens)
            - Resource Owner Password Credentials Grant (also indirectly)
            - Refresh Token Grant
        """
        token = self.storage.get_token(refresh_token=refresh_token)
        if token and token.get_client_id() == client.get_id():
            # Make sure the request object contains user and client_id
            request.client_id = token.get_client_id()
            request.user = token.get_user()
            return True
        return False

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        """Ensure client is authorized to use the response_type requested.

        :param client_id: Unicode client identifier
        :param response_type: Unicode response type, i.e. code, token.
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        if response_type not in ('code', 'token'):
            return False

        if hasattr(client, 'allowed_response_types'):
            return response_type in client.allowed_response_types
        return True

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """Ensure the client is authorized access to requested scopes.

        :param client_id: Unicode client identifier
        :param scopes: List of scopes (defined by you)
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by all core grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials Grant
        """
        if hasattr(client, 'validate_scopes'):
            return client.validate_scopes(scopes)
        return set(client.get_default_scopes()).issuperset(set(scopes))

    def validate_user(self, username, password, client, request, *args, **kwargs):
        """Ensure the username and password is valid.

        OBS! The validation should also set the user attribute of the request
        to a valid resource owner, i.e. request.user = username or similar. If
        not set you will be unable to associate a token with a user in the
        persistance method used (commonly, save_bearer_token).

        :param username: Unicode username
        :param password: Unicode password
        :param client: Client object set by you, see authenticate_client.
        :param request: The HTTP Request (oauthlib.common.Request)
        :rtype: True or False

        Method is used by:
            - Resource Owner Password Credentials Grant
        """
        log.debug("Validating username %r and password %r", username, password)
        user = self.storage.auth_user(username, password)
        if user:
            request.user = user
            return True
        log.debug('Password credential authorization is disabled.')
        return False

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        """Revoke an access or refresh token.

        :param token: The token string.
        :param token_type_hint: access_token or refresh_token.
        :param request: The HTTP Request (oauthlib.common.Request)

        Method is used by:
            - Revocation Endpoint
        """
        if token_type_hint:
            oauth_token = self.storage.get_token(**{token_type_hint: token})
        else:
            oauth_token = self.storage.get_token(access_token=token)
            if not oauth_token:
                oauth_token = self.storage.get_token(refresh_token=token)

        if oauth_token and oauth_token.get_client_id() == request.client.get_id():
            request.client_id = oauth_token.get_client_id()
            request.user = oauth_token.get_user()
            self.storage.delete_token(oauth_token)
            return True

        request.error_message = "Invalid token supplied."
        log.debug("revoke_token error: %r.", request.error_message)
        return False
