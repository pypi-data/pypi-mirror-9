import logging


class DefaultPersistencePolicy(object):

    def persist(self, data):
        pass


class ExternalApiPersistencePolicy(DefaultPersistencePolicy):
    api_url = ''

    def get_api_url(self, **kwargs):
        return self.api_url

    def persist(self, data):
        pass


class RQPersistencePolicy(DefaultPersistencePolicy):

    def persist(self, data):
        pass