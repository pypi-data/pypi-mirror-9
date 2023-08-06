# coding=utf8

import re
import time
import warnings
import requests
import asyncio
from functools import partial

from urllib.parse import urlparse, parse_qsl
import json


REDIRECT_URI = 'https://oauth.vk.com/blank.html'

# vk.com API Errors
AUTHORIZATION_FAILED = 5  # Invalid access token
CAPTCHA_IS_NEEDED = 14


def json_iter_parse(response_text):
    decoder = json.JSONDecoder(strict=False)
    idx = 0
    while idx < len(response_text):
        obj, idx = decoder.raw_decode(response_text, idx)
        yield obj


class APISession(object):
    def __init__(self, app_id=None, user_login=None, user_password=None, access_token=None,
                 scope='offline', timeout=1, api_version='5.28', loop=None):


        self.loop = loop or asyncio.get_event_loop()
        self.app_id = app_id
        self.user_login = user_login
        self.user_password = user_password
        self.access_token = access_token

        self.scope = scope
        self.api_version = api_version
        self.default_timeout = timeout

        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/json'
        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    @asyncio.coroutine
    def get_access_token(self):
        if self.user_login and not self.user_password:
            # Need user password
            pass

        if not self.user_login and self.user_password:
            # Need user login
            pass

        session = requests.Session()

        # Login
        login_data = {
            'act': 'login',
            'utf8': '1',
            'email': self.user_login,
            'pass': self.user_password,
            'redirect_uri': REDIRECT_URI
        }

        response = yield from self.loop.run_in_executor(
            None,
            session.post,
            'https://login.vk.com',
            login_data
        )

        if 'remixsid' in session.cookies or 'remixsid6' in session.cookies:
            pass
        elif 'sid=' in response.url:
            self.auth_captcha_is_needed(response.content, session)
        elif 'act=authcheck' in response.url:
            self.auth_code_is_needed(response.content, session)
        elif 'security_check' in response.url:
            self.phone_number_is_needed(response.content, session)
        else:
            raise VkAuthorizationError('Authorization error (bad password)')

        # OAuth2
        oauth_data = {
            'response_type': 'token',
            'client_id': self.app_id,
            'scope': self.scope,
            'display': 'mobile',
            }
        response = yield from self.loop.run_in_executor(
            None,
            session.post,
            'https://oauth.vk.com/authorize',
            oauth_data
        )

        if 'access_token' not in response.url:
            form_action = re.findall(u'<form method="post" action="(.+?)">', response.text)
            if form_action:
                response = yield from self.loop.run_in_executor(
                    None,
                    session.get,
                    form_action[0]
                )
            else:
                try:
                    json_data = response.json()
                except ValueError:  # not json in response
                    error_message = 'OAuth2 grant access error'
                else:
                    error_message = 'VK error: [{0}] {1}'.format(
                        json_data['error'],
                        json_data['error_description']
                    )
                session.close()
                raise VkAuthorizationError(error_message)

        session.close()

        parsed_url = urlparse(response.url)
        token_dict = dict(parse_qsl(parsed_url.fragment))
        if 'access_token' in token_dict:
            self.access_token = token_dict['access_token']
            self.expires_in = token_dict['expires_in']
        else:
            raise VkAuthorizationError('OAuth2 authorization error')
        return self.access_token

    def __getattr__(self, method_name):
        return APIMethod(self, method_name)

    @asyncio.coroutine
    def __call__(self, method_name, **method_kwargs):

        response = yield from self.method_request(method_name, **method_kwargs)
        response.raise_for_status()

        # there are may be 2 dicts in 1 json
        # for example: {'error': ...}{'response': ...}
        errors = []
        error_codes = []
        for data in json_iter_parse(response.text):
            if 'error' in data:
                error_data = data['error']
                if error_data['error_code'] == CAPTCHA_IS_NEEDED:
                    return self.captcha_is_needed(error_data, method_name, **method_kwargs)

                error_codes.append(error_data['error_code'])
                errors.append(error_data)

            if 'response' in data:
                for error in errors:
                    warnings.warn(str(error))

                return data['response']

        if AUTHORIZATION_FAILED in error_codes:  # invalid access token
            self.access_token = None
            yield from self.get_access_token()
            response = yield from self(method_name, **method_kwargs)
            return response
        else:
            raise VkAPIMethodError(errors[0])
    def captcha_is_needed(self, error_data, method_name, **method_kwargs):
        """
        Default behavior on CAPTCHA is to raise exception
        Reload this in child
        """
        raise VkAPIMethodError(error_data)


    @asyncio.coroutine
    def method_request(self, method_name, timeout=None, **method_kwargs):
        if self.access_token is None and (self.user_login and self.user_password):
            yield from self.get_access_token()

        params = dict(
            timestamp=int(time.time()),
            v=self.api_version,
            access_token=self.access_token
        )

        params.update(method_kwargs)
        url = 'https://api.vk.com/method/' + method_name

        response = yield from self.loop.run_in_executor(
            None,
            partial(self.session.post, timeout=timeout or self.default_timeout),
            url,
            params
        )
        return response

    def auth_code_is_needed(self, content, session):
        """
        Default behavior on 2-AUTH CODE is to raise exception
        Reload this in child
        """
        raise VkAuthorizationError('Authorization error (2-factor code is needed)')

    def auth_captcha_is_needed(self, content, session):
        """
        Default behavior on CAPTCHA is to raise exception
        Reload this in child
        """
        raise VkAuthorizationError('Authorization error (captcha)')

    def phone_number_is_needed(self, content, session):
        """
        Default behavior on PHONE NUMBER is to raise exception
        Reload this in child
        """
        raise VkAuthorizationError('Authorization error (phone number is needed)')


class APIMethod(object):
    __slots__ = ['_api_session', '_method_name']

    def __init__(self, api_session, method_name):
        self._api_session = api_session
        self._method_name = method_name

    def __getattr__(self, method_name):
        return APIMethod(self._api_session, self._method_name + '.' + method_name)

    @asyncio.coroutine
    def __call__(self, **method_kwargs):
        response = yield from self._api_session(self._method_name, **method_kwargs)
        return response


class VkError(Exception):
    pass


class VkAuthorizationError(VkError):
    pass


class VkAPIMethodError(VkError):
    __slots__ = ['error', 'code', 'message', 'request_params', 'redirect_uri']

    def __init__(self, error):
        super(VkAPIMethodError, self).__init__()
        self.error = error
        self.code = error.get('error_code')
        self.message = error.get('error_msg')
        self.request_params = error.get('request_params')
        self.redirect_uri = error.get('redirect_uri')

    def __str__(self):
        error_message = '{self.code}. {self.message}. request_params = {self.request_params}'.format(self=self)
        if self.redirect_uri:
            error_message += ',\nredirect_uri = "{self.redirect_uri}"'.format(self=self)
        return error_message
