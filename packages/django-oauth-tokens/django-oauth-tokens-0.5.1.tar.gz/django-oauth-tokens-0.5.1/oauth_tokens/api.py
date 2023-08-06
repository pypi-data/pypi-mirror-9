# -*- coding: utf-8 -*-
from httplib import BadStatusLine
import logging
import socket
from ssl import SSLError
import time

from abc import abstractmethod, abstractproperty, ABCMeta
from requests.exceptions import ConnectionError
from .models import AccessToken, AccessTokenGettingError, AccessTokenRefreshingError

__all__ = ['NoActiveTokens', 'ApiAbstractBase', 'Singleton']


class NoActiveTokens(Exception):
    pass


class ApiAbstractBase(object):
    __metaclass__ = ABCMeta

    consistent_token = None
    error_class = Exception
    error_class_repeat = (SSLError, ConnectionError, socket.error, BadStatusLine)
    sleep_repeat_error_messages = []

    recursion_count = 0

    method = None
    token_tag = None
    token_tag_arg_name = 'methods_access_tag'
    used_access_tokens = None

    update_tokens_max_count = 5
    refresh_tokens_max_count = 5

    def __init__(self):
        self.used_access_tokens = []
        self.consistent_token = self.get_consistent_token()
        self.logger = self.get_logger()
        self.api = None

    def call(self, method, *args, **kwargs):
        self.method = method
        self.token_tag = kwargs.pop(self.token_tag_arg_name, None)

        try:
            token = self.get_token(tag=self.token_tag)
        except NoActiveTokens, e:
            return self.handle_error_no_active_tokens(e, *args, **kwargs)

        self.api = self.get_api(token)

        try:
            response = self.get_api_response(*args, **kwargs)
        except self.error_class, e:
            response = self.handle_error_message(e, *args, **kwargs)
            if response is not None:
                return response
            response = self.handle_error_code(e, *args, **kwargs)
        except self.error_class_repeat, e:
            response = self.handle_error_repeat(e, *args, **kwargs)
        except Exception, e:
            self.logger.error(
                "Unhandled error: %s registered while executing method %s with params %s" % (e, self.method, kwargs))
            raise

        return response

    def handle_error_no_active_tokens(self, e, *args, **kwargs):
        if self.used_access_tokens:
            # wait 1 sec and repeat with empty used_access_tokens
            self.logger.warning("Waiting 1 sec, because all active tokens are used, method: %s, recursion count: %d" %
                                (self.method, self.recursion_count))
            self.used_access_tokens = []
            return self.sleep_repeat_call(*args, **kwargs)
        else:
            self.logger.warning("Suddenly updating tokens, because no active access tokens and used_access_tokens "
                                "empty, method: %s, recursion count: %d" % (self.method, self.recursion_count))
            self.update_tokens()
            return self.repeat_call(*args, **kwargs)

    def handle_error_message(self, e, *args, **kwargs):
        # check if error message contains any of defined messages
        for message in self.sleep_repeat_error_messages:
            if message in str(e):
                return self.sleep_repeat_call(*args, **kwargs)
        return

    def handle_error_code(self, e, *args, **kwargs):
        # try to find method for handling exception by it's code
        try:
            return getattr(self, 'handle_error_code_%d' % self.get_error_code(e))(e, *args, **kwargs)
        except AttributeError:
            self.logger.error("Recognized unhandled error: %s registered while executing method %s with params %s"
                              % (e, self.method, kwargs))
            raise e

    def get_error_code(self, e):
        return e.code

    def handle_error_repeat(self, e, *args, **kwargs):
        self.logger.error("Exception: '%s' registered while executing method %s with params %s, recursion count: %d"
                          % (e, self.method, kwargs, self.recursion_count))
        return self.sleep_repeat_call(*args, **kwargs)

    def sleep_repeat_call(self, seconds=1, *args, **kwargs):
        time.sleep(seconds)
        return self.repeat_call(*args, **kwargs)

    def repeat_call(self, *args, **kwargs):
        self.recursion_count += 1
        if self.token_tag:
            kwargs[self.token_tag_arg_name] = self.token_tag
        return self.call(self.method, *args, **kwargs)

    def update_tokens(self):
        self.consistent_token = None
        try:
            return AccessToken.objects.fetch(provider=self.provider)
        except AccessTokenGettingError:
            if self.recursion_count <= self.update_tokens_max_count:
                time.sleep(1)
                self.recursion_count += 1
                self.update_tokens()
            else:
                raise

    def refresh_tokens(self):
        if self.consistent_token:
            self.update_tokens()
        else:
            try:
                return AccessToken.objects.refresh(self.provider)
            except AccessTokenRefreshingError:
                if self.recursion_count <= self.refresh_tokens_max_count:
                    time.sleep(1)
                    self.recursion_count += 1
                    self.refresh_tokens()
                else:
                    raise

    def get_tokens(self, **kwargs):
        return AccessToken.objects.filter(provider=self.provider, **kwargs).order_by('-granted_at')

    def get_token(self, **kwargs):
        token = None

        if self.consistent_token not in self.used_access_tokens:
            token = self.consistent_token

        if not token:
            tokens = self.get_tokens(**kwargs)

            if not tokens:
                self.update_tokens()
                tokens = self.get_tokens(**kwargs)

            if self.used_access_tokens:
                tokens = tokens.exclude(access_token__in=self.used_access_tokens)

            try:
                token = tokens[0].access_token
            except IndexError:
                raise NoActiveTokens("There is no active AccessTokens for provider %s with kwargs: %s, used_tokens: %s"
                                     % (self.provider, kwargs, self.used_access_tokens))

        return token

    def get_consistent_token(self):
        pass

    def get_logger(self):
        return logging.getLogger('%s_api' % self.provider)

    @abstractproperty
    def provider(self):
        pass

    @abstractmethod
    def get_api(self, token):
        pass

    @abstractmethod
    def get_api_response(self):
        pass


class Singleton(ABCMeta):
    """
    Singleton metaclass for API classes
    from here http://stackoverflow.com/a/33201/87535
    """

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance
