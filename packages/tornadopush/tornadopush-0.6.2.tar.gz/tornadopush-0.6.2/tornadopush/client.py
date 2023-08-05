import json
from itsdangerous import URLSafeTimedSerializer
from redis import StrictRedis


class Channel(object):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel

    def emit(self, event, data=None, target=None, serialize=True):
        if serialize:
            data = json.dumps(data)
        event_data = '%s;%s;%s' % (event, target or "", data)
        self.client.publish(self.channel, event_data)


class EventEmitter(object):
    def __init__(self, client, secret_key='tornadopush'):
        self.client = client
        self.token_serializer = URLSafeTimedSerializer(secret_key)

    def create_token(self, user_id, allowed_channels=None):
        return self.token_serializer.dumps([user_id, allowed_channels])

    def channel(self, name):
        return Channel(self.client, name)

    def emit(self, channel, event, data=None, target=None, serialize=True):
        self.channel(channel).emit(event, data, target, serialize)


_emitter = None

def connect(url=None, secret_key='tornadopush'):
    global _emitter
    if isinstance(url, StrictRedis):
        client = url
    elif url:
        client = StrictRedis.from_url(url)
    else:
        client = StrictRedis()
    _emitter = EventEmitter(client, secret_key)


def emit(channel, event, data=None, target=None, serialize=True):
    _emitter.emit(channel, event, data, target, serialize)