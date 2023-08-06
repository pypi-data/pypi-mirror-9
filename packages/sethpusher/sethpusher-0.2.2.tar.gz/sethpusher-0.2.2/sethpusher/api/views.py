import json
import logging

import tornado.gen
import tornado.web

from sethpusher import utils


class SethHandler(tornado.web.RequestHandler):

    def json_response(self, data, code=200):
        data["status"] = code
        self.write(json.dumps(data) + "\n")
        self.set_status(code)

    def error(self, message, code=500):
        self.json_response({"message": message}, code)

    def prepare(self):
        authenticator = self.application.authentication_policy
        if authenticator and not authenticator.authenticate(self.request):
            self.error(u"Invalid Auth credentials provided", 401)
            self.finish()


class OverallDebugHandler(SethHandler):

    @tornado.gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json')

        count = self.application.get_subscriber_count(channel=None)
        subscribers = self.application.get_subscribers(channel=None)

        text = json.dumps({
            'subscriber_count': count,
            'subscribers': subscribers
        })
        self.write(text)


class ChannelDebugHandler(SethHandler):

    @tornado.gen.coroutine
    def get(self, channel):
        self.set_header('Content-Type', 'application/json')

        count = self.application.get_subscriber_count(channel=channel)
        subscribers = self.application.get_subscribers(channel=channel)

        text = json.dumps({
            'subscriber_count': count,
            'subscribers': subscribers
        })
        self.write(text)


class UserHandler(SethHandler):

    @utils.is_request_body_json
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        user = kwargs['user']
        msg = json.loads(self.request.body)

        self.application.persist(msg, user=user)
        self.application.send_to_user(msg=msg, user=user)

        logging.info(u"Message has been send to user: {0}".format(user))
        return self.json_response({'status': True})


class ChannelHandler(SethHandler):

    @utils.is_request_body_json
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        channel = kwargs['channel']
        msg = json.loads(self.request.body)

        self.application.persist(msg, channel=channel)
        self.application.send_to_channel(msg=msg, channel=channel)

        logging.debug(u"Message has been send to channel: {0}".format(channel))
        return self.json_response({'status': True})
