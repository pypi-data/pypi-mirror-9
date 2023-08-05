from tornado.websocket import WebSocketHandler, WebSocketClosedError
from .base import *


class User(object):
    def __init__(self, uid, meta=None, handler=None):
        self.uid = uid
        self.meta = meta or '{}'
        self.handlers = []
        if handler:
            self.handlers.append(handler)

    def send(self, msg):
        for handler in self.handlers:
            if handler.ws_connection:
                handler.handle_presence(msg)


class Channel(object):
    def __init__(self, name):
        self.name = name
        self.users = {}

    def broadcast(self, msg, ignore_user=None):
        for user in self.users.itervalues():
            if not ignore_user or user.uid != ignore_user:
                user.send("%s:%s" % (self.name, msg))

    def broadcast_msg(self, from_uid, msg):
        self.broadcast('bcast:%s;%s' % (from_uid, msg), from_uid)
        logger.debug('Presence: broadcast from %s on #%s: %s' % (from_uid, self.name, msg))

    def join(self, uid, handler, meta=None):
        if uid not in self.users:
            self.users[uid] = User(uid, meta, handler)
            self.broadcast("+:%s;%s" % (uid, self.users[uid].meta), uid)
            logger.debug('Presence: %s joined #%s' % (uid, self.name))
        else:
            self.users[uid].handlers.append(handler)
            if meta:
                self.set_meta(uid, meta)

    def set_meta(self, uid, meta):
        self.users[uid].meta = meta
        self.broadcast("meta:%s;%s" % (uid, meta), uid)
        logger.debug('Presence: meta for %s on #%s: %s' % (uid, self.name, meta))

    def leave(self, uid, handler):
        if uid not in self.users:
            return
        user = self.users[uid]
        user.handlers.remove(handler)
        if not user.handlers:
            del self.users[uid]
            self.broadcast("-:%s" % uid, uid)
            logger.debug('Presence: %s left #%s' % (uid, self.name))

    def send_user_list(self, handler, ignore_user=None):
        for user in self.users.itervalues():
            if not ignore_user or user.uid != ignore_user:
                handler.handle_presence("%s:+:%s;%s" % (self.name, user.uid, user.meta))


CHANNELS = {}
def get_channel(name):
    if name not in CHANNELS:
        CHANNELS[name] = Channel(name)
    return CHANNELS[name]


class PresenceMixin(object):
    def notify_join(self, channel, meta=None):
        if channel not in self.presence_channels:
            if self.user_channels and channel not in self.user_channels:
                return None
            self.presence_channels[channel] = get_channel(channel)
            self.presence_channels[channel].join(self.user_id, self, meta)
            self.send_presence_user_list(channel)
        return self.presence_channels[channel]

    def notify_leave(self, channel):
        if channel in self.presence_channels:
            self.presence_channels[channel].leave(self.user_id, self)
            del self.presence_channels[channel]

    def notify_leave_all(self):
        for channel in self.presence_channels.itervalues():
            channel.leave(self.user_id, self)
        self.presence_channels = {}

    def send_presence_user_list(self, channel):
        ch = self.notify_join(channel)
        if ch:
            ch.send_user_list(self, self.user_id)

    def on_presence_message(self, msg):
        channel, action, data = msg.split(':', 2)
        if action == 'join':
            self.notify_join(channel, data)
        elif action == 'leave':
            self.notify_leave(channel)
        elif action == 'bcast':
            ch = self.notify_join(channel)
            if ch:
                ch.broadcast_msg(self.user_id, data)
        elif action == 'meta':
            ch = self.notify_join(channel)
            if ch:
                ch.set_meta(self.user_id, data)
        elif action == 'users':
            self.send_presence_user_list(channel)

    def handle_presence(self, msg):
        try:
            self.write_message("presence:%s" % msg)
        except WebSocketClosedError:
            pass


class PresenceHandler(PresenceMixin, AuthentifyMixin, WebSocketMixin, WebSocketHandler):

    def __init__(self, *args, **kwargs):
        WebSocketHandler.__init__(self, *args, **kwargs)
        self.presence_channels = {}
        self.channel = None
        self.auth_done = False

    def open(self):
        self.authentify(self.get_argument('token', None))

    def on_authorized(self):
        AuthentifyMixin.on_authorized(self)
        self.start_heartbeat()

    def on_message(self, message):
        if not self.auth_done:
            return
        if message.startswith('presence:'):
            self.on_presence_message(message[9:])

    def on_close(self):
        self.notify_leave_all()