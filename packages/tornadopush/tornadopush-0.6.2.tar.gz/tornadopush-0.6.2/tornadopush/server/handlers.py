import tornado.web
import tornado.websocket
import tornado.httpclient
from .base import *
from .queue import QueueMixin
from .presence import PresenceMixin
import json


class BaseMixin(PresenceMixin, ChannelMixin, AuthentifyMixin, QueueMixin):
    @property
    def presence_enabled(self):
        return self.get_argument('presence', None) == '1'

    def open(self, channel=None):
        self.channel = channel
        self.authentify(self.get_argument('token', None))

    def on_authorized(self):
        AuthentifyMixin.on_authorized(self)
        if self.presence_enabled:
            self.notify_join(self.channel)
        self.subscribe(self.channel_key)

    def on_event_message(self, msg):
        event, target, data = msg.split(';', 2)
        if target and target != self.user_id:
            logger.debug('Ignored event: %s' % event)
            return
        logger.debug('Event received: %s' % event)
        self.handle_event(event, data)

    on_queue_message = on_event_message

    def on_message(self, message):
        if self.application.settings['publish_method'] == 'queue':
            self.publish_queue_message(self.channel, message)
        elif self.application.settings['publish_method'] == 'webhook':
            webhook_url = self.application.settings['webhook_url']
            if not webhook_url:
                logger.error('Missing webhook url!')
            logger.debug("Message from client: %s" % message)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(webhook_url,
                method='POST',
                headers={"Content-Type": "application/json"},
                body=json.dumps({
                    "channel": self.channel,
                    "user_id": self.user_id,
                    "message": message}))

    def handle_event(self, event, data):
        raise NotImplementedError

    def do_close(self, callback=None):
        self.notify_leave_all()
        self.close_queue_client(callback)


class SSEHandler(BaseMixin, tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)
        self.presence_channels = {}
        self.auth_done = False

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')

    @tornado.web.asynchronous
    def get(self, channel=None):
        self.set_header('Content-Type','text/event-stream; charset=utf-8')
        self.set_header('Cache-Control','no-cache')
        self.set_header('Connection','keep-alive')
        self.open(channel)

    @tornado.web.asynchronous
    def post(self, channel=None):
        self.channel = channel
        def on_auth():
            self.on_message(self.request.body)
            self.finish()
        self.authentify(self.get_argument('token', None), callback=on_auth)

    def options(self, *args, **kwargs):
        self.finish()

    def on_authorized(self):
        self.flush() # send headers
        BaseMixin.on_authorized(self)

    def on_queue_disconnect(self):
        self.finish()

    def handle_event(self, event, data):
        self.write("event: {0}\ndata: {1}\n\n".format(event, data))
        self.flush()

    def handle_presence(self, msg):
        self.handle_event("__presence__", msg)

    def on_connection_close(self):
        self.do_close(lambda: super(SSEHandler, self).on_connection_close())


class WebSocketHandler(BaseMixin, WebSocketMixin, tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, *args, **kwargs)
        self.presence_channels = {}
        self.auth_done = False

    def on_authorized(self):
        BaseMixin.on_authorized(self)
        self.start_heartbeat()

    def on_queue_disconnect(self):
        self.close()
        self.on_close()

    def handle_event(self, event, data):
        try:
            self.write_message("event:%s;%s" % (event, data))
        except tornado.websocket.WebSocketClosedError:
            pass

    def on_message(self, message):
        if not self.auth_done:
            return
        if message.startswith('presence:'):
            self.on_presence_message(message[9:])
        elif message.startswith('message:'):
            BaseMixin.on_message(self, message[8:])

    def on_close(self):
        self.do_close()
