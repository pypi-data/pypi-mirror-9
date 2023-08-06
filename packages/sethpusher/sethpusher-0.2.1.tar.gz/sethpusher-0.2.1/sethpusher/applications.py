from tornado.web import Application

from sethpusher import mixins
from sethpusher import persistors
from sethpusher import dispatchers
from sethpusher import authenticators
from sethpusher.ws.urls import get_ws_handlers
from sethpusher.api.urls import get_api_handlers


class DefaultSethApplication(Application):
    authentication_policy = None
    persistence_policy = None

    def get_dispatcher(self):
        return dispatchers.DefaultMessageDispatcher()

    def get_authentication_policy(self, **kwargs):
        return authenticators.EchoAuthenticationPolicy()

    def get_persistence_policy(self, **kwargs):
        return persistors.DefaultPersistencePolicy()

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        handlers = get_api_handlers(self) + get_ws_handlers(self)
        self.subscriber = self.get_subscriber(**kwargs)
        self.publisher = self.get_publisher(**kwargs)
        self.authentication_policy = self.get_authentication_policy(**kwargs)
        self.persistence_policy = self.get_persistence_policy(**kwargs)
        super(DefaultSethApplication, self).__init__(handlers, **kwargs)


class SethPusherOnRedisApplication(DefaultSethApplication,
                                   mixins.RedisPubSubMixin):

    pass


class SethPusherInMemoryApplication(DefaultSethApplication,
                                    mixins.InMemoryPubSubMixin):

    pass