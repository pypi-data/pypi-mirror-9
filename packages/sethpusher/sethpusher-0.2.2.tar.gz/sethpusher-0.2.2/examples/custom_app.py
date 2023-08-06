import logging

from tornado.options import parse_command_line

from sethpusher.default_server import AppRunner
from sethpusher.applications import SethPusherInMemoryApplication
from sethpusher.authenticators import ApiKeyAuthenticationPolicy
from sethpusher.persistors import ExternalApiPersistencePolicy


class MyPersistence(ExternalApiPersistencePolicy):
    api_url = 'http://www.my_super_api.com'

    def persist(self, data, **kwargs):
        print data
        print kwargs
        print "KABOOM !"


class MyAuth(ApiKeyAuthenticationPolicy):
    key_name = u'batman'
    key_secret_value = u'bruce_wayne'


class MyVeryOwnApp(SethPusherInMemoryApplication):

    def get_authentication_policy(self, **kwargs):
        return MyAuth()

    def get_persistence_policy(self, **kwargs):
        return MyPersistence()


if __name__ == '__main__':
    parse_command_line()
    logging.debug(u"DEBUG IS ON")
    runner = AppRunner(port=8080, debug=True)
    runner.start(app=MyVeryOwnApp)