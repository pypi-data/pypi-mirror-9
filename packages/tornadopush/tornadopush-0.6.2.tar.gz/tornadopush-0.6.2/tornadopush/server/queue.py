import tornadoredis
import toredis
from .base import logger


class BaseClient(object):
    def __init__(self):
        self.disconnect_callback = None
        self.subscribed = False
        self.subscribed_to = []

    def subscribe(self, channels, listener, callback=None):
        raise NotImplementedError

    def unsubscribe(self, callback=None):
        pass

    def close(self, callback=None):
        self.unsubscribe(callback)

    def set_disconnect_callback(self, callback):
        self.disconnect_callback = callback


class TornadoRedisQueueClient(BaseClient):
    def __init__(self, app):
        super(TornadoRedisQueueClient, self).__init__()
        self.listener = None
        self.client = tornadoredis.Client(app.settings['redis_host'], app.settings['redis_port'],
            app.settings['redis_password'], app.settings['redis_db'])
        self.client.connect()

    def subscribe(self, channels, listener, callback=None):
        self.listener = listener
        def on_subscribe(*args):
            self.client.listen(self.on_message)
            self.subscribed = True
            self.subscribed_to = channels
            if callback:
                callback()
        self.client.subscribe(channels, on_subscribe)

    def on_message(self, msg):
        if msg.kind == 'disconnect':
            logger.debug('Listener has received disconnect')
            if self.disconnect_callback:
                self.disconnect_callback()
            return
        if msg.kind in ('subscribe', 'unsubscribe'):
            return
        if self.listener:
            self.listener(str(msg.body))

    def unsubscribe(self, callback=None):
        if not self.subscribed:
            if callback:
                callback()
            return
        def cb():
            self.subscribed = False
            if callback:
                callback()
        self.client.unsubscribe(self.subscribed_to, callback=cb)

    def close(self, callback=None):
        def on_unsubscribe(*args):
            self.client.disconnect()
            logger.debug('Client disconnected')
            if callback:
                callback()
        if self.subscribed:
            self.unsubscribe(on_unsubscribe)
        else:
            on_unsubscribe()


class TornadoRedisQueue(object):
    def __init__(self, app):
        self.app = app

    def create_client(self):
        return TornadoRedisQueueClient(self.app)

    def publish(self, channel, message):
        pass


class ToRedisQueueClient(BaseClient):
    def __init__(self, app):
        super(ToRedisQueueClient, self).__init__()
        self.listener = None
        self.client = toredis.Client()
        self.client.connect(host=app.settings['redis_host'], port=app.settings['redis_port'])
        self.closing = False

    def subscribe(self, channels, listener, callback=None):
        self.listener = listener
        self.client.subscribe(channels, callback=self.on_message)
        self.subscribed = True
        self.subscribed_to = channels
        if callback:
            callback()

    def on_message(self, msg):
        if not msg:
            if self.closing:
                return
            logger.debug('Listener has received disconnect')
            if self.disconnect_callback:
                self.disconnect_callback()
            return
        msg_type, msg_channel, msg_value = msg
        if msg_type == 'message' and self.listener:
            self.listener(str(msg_value))

    def unsubscribe(self, callback=None):
        if not self.subscribed:
            if callback:
                callback()
            return
        def cb():
            self.subscribed = False
            if callback:
                callback()
        self.client.unsubscribe(self.subscribed_to, callback=cb)

    def close(self, callback=None):
        self.closing = True
        self.client._stream.close()
        logger.debug('Client disconnected')
        if callback:
            callback()


class ToRedisQueue(object):
    def __init__(self, app):
        self.app = app

    def create_client(self):
        return ToRedisQueueClient(self.app)

    def publish(self, channel, message):
        pass


class LocalQueueClient(BaseClient):
    def __init__(self, queue):
        super(LocalQueueClient, self).__init__()
        self.queue = queue
        self.listener = None

    def subscribe(self, channels, listener, callback=None):
        self.listener = listener
        for channel in channels:
            self.queue.channels.setdefault(channel, []).append(listener)
        self.subscribed = True
        self.subscribed_to = channels
        if callback:
            callback()

    def unsubscribe(self, callback=None):
        for channel in self.subscribed_to:
            self.queue.channels.get(channel, []).remove(self.listener)
        self.subscribed = False
        if callback:
            callback()


class LocalQueue(object):
    def __init__(self, app):
        self.app = app
        self.channels = {}

    def create_client(self):
        return LocalQueueClient(self)

    def publish(self, channel, message):
        for listener in self.channels.get(channel, []):
            listener(message)


queue_providers = {"tornado_redis": TornadoRedisQueue,
                   "toredis": ToRedisQueue,
                   "local": LocalQueue}


class QueueMixin(object):
    queue_client = None

    def subscribe(self, *channels):
        self.queue_client = self.application.queue_provider.create_client()
        self.queue_client.set_disconnect_callback(self.on_queue_disconnect)
        self.queue_client.subscribe(channels, self.on_queue_message)

    def unsubscribe(self, callback=None):
        if self.queue_client:
            self.queue_client.unsubscribe(callback)

    def publish_queue_message(self, channel, msg):
        self.application.queue_provider.publish(channel, msg)

    def on_queue_disconnect(self):
        pass

    def close_queue_client(self, callback=None):
        if self.queue_client:
            self.queue_client.close(callback)
