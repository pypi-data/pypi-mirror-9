#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

from functools import wraps
import json
import requests
from .auth.client_credentials import ClientCredentialsMixin

class FinFeedClient(ClientCredentialsMixin):

    API_ROOT = "http://api.finfeed.io"
    HTTP_METHODS = {'head', 'get', 'post'}
    ACCEPT_HEADER = "application/vnd.finfeed.*;version=0.1"
    USER_AGENT = "pyfinfeed 0.1;"

    def __init__(self, token=None, key=None, secret=None, *args, **kwargs):
        self.token = token
        self.app_info = (key, secret)
        self._requests_methods = dict()

        assert token is not None or (key is not None and secret is not None)

    @property
    def token(self):
        return self._token.token
    @token.setter
    def token(self, value):
        self._token = _BearerToken(value) if value else None

    def __getattr__(self, name):
        
        if name not in self.HTTP_METHODS:
            raise AttributeError("%r is not an allowed HTTP method" % name)

        request_func = getattr(requests, name, None)
        if request_func is None:
            raise AttributeError("%r could not be found in the backing lib"
                % name)

        @wraps(request_func)
        def caller(url, jsonify=True, **kwargs):

            headers = kwargs.get('headers', dict())
            headers['Accept'] = self.ACCEPT_HEADER
            headers['User-Agent'] = self.USER_AGENT

            if jsonify \
                    and 'data' in kwargs \
                    and isinstance(kwargs['data'], (dict, list)):
                kwargs['data'] = json.dumps(kwargs['data'])
                headers['Content-Type'] = 'application/json'

            kwargs['timeout'] = kwargs.get('timeout', 30)
            kwargs['auth'] = kwargs.get('auth', self._token)
            kwargs['headers'] = headers

            # support for batching
            params = kwargs.get('params')
            if kwargs.get('params') is not None:
                params = kwargs.get('params')

                output = {}
                for i,a in enumerate(params):
                    if isinstance(params[a], list):

                        # we need to cast ints to string
                        # for the url params
                        if isinstance(params[a][0], int):
                            params[a] = [str(param) for param in params[a]]

                        output[a] = "+".join(params[a])
                    else:
                        output[a] = params[a]
                kwargs['params'] = output

            if not url[:4] == "http":
                url = self.API_ROOT + url

            print url
            return request_func(
                url,
                **kwargs)

        return caller

class _BearerToken(requests.auth.AuthBase):
    
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer ' + self.token
        return request
