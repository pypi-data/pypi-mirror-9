import tornado.ioloop
import tornado.httpserver
import tornado.web
import os
import tempfile
from itsdangerous import URLSafeTimedSerializer
from .handlers import SSEHandler, WebSocketHandler
from .presence import PresenceHandler
from .base import logger
from .queue import queue_providers
from tornadopush.assets import generate_bundle, generate_authentication_code


class JsClientHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/javascript')
        token = self.get_argument('token', None)
        if not token:
            content = self.generate_default_bundle()
        else:
            content = self.generate_tokenized_bundle(token)
        self.write(content)
        self.finish()

    def generate_default_bundle(self):
        tmpfilename = os.path.join(self.application.settings['assets_cache_path'], 'bundle.js')
        if not os.path.exists(tmpfilename):
            content = generate_bundle(host=self.request.host)
            with open(tmpfilename, 'w') as f:
                f.write(content)
            logger.debug('Bundle file written to %s' % tmpfilename)
            return content
        with open(tmpfilename) as f:
            return f.read()

    def generate_tokenized_bundle(self, token):
        content = self.generate_default_bundle()
        content += generate_authentication_code(token)
        return content


class Application(tornado.web.Application):
    default_settings = {
        'queue': 'tornado_redis',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_password': None,
        'redis_db': None,
        'token_secret': 'tornadopush',
        'auth_enabled': False,
        'channel_format': '%s',
        'presence_channel': 'presence:%s',
        'presence_users_key': 'presence_users:%s',
        'token_max_age': 3600,
        'allowed_channels': None,
        'default_channel': 'tornado',
        'publish_method': None,
        'webhook_url': None,
        'assets_cache_path': None
    }

    def __init__(self, default_host="", transforms=None, **settings):
        static_path = os.path.join(os.path.dirname(__file__), '../static')
        handlers = [
            (r"/tornadopush.js", JsClientHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
            (r"/channel/([a-zA-Z_0-9]+)", WebSocketHandler),
            (r"/channel/([a-zA-Z_0-9]+)\.sse", SSEHandler),
            (r"/presence", PresenceHandler)]
        super(Application, self).__init__(handlers, default_host, transforms,
            **dict(self.default_settings, **settings))
        self.token_serializer = URLSafeTimedSerializer(self.settings["token_secret"])
        self.queue_provider = queue_providers[self.settings['queue']](self)
        logger.debug('Using queue provider: %s' % self.settings['queue'])
        if not self.settings['assets_cache_path']:
            self.settings['assets_cache_path'] = tempfile.mkdtemp()


def create_server(port=8888, **settings):
    server = tornado.httpserver.HTTPServer(Application(**settings))
    server.listen(port)
    return server


def start_server(port=8888, **settings):
    server = create_server(port, **settings)
    tornado.ioloop.IOLoop.instance().start()
