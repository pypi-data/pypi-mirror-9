import logging

from tornado.httpclient import AsyncHTTPClient


class DefaultPersistencePolicy(object):
    """
        Provides interface to persistence policies.
    """
    def persist(self, data, **kwargs):
        pass


class ExternalApiPersistencePolicy(DefaultPersistencePolicy):
    """
        Posts message to selected API endpoint using AsyncHTTPClient
    """
    api_url = ''

    def get_api_url(self, **kwargs):
        return self.api_url

    def persist(self, data, **kwargs):
        pass


class RedisPersistencePolicy(DefaultPersistencePolicy):
    """
        Stores messages in redis
    """
    def persist(self, data, **kwargs):
        pass