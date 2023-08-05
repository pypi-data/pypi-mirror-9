from .server import start_server, logger
import logging
import yaml
import argparse
import os
import signal
import tornado.ioloop


is_closing = False
logging.basicConfig()


def signal_handler(signum, frame):
    global is_closing
    print "Closing..."
    is_closing = True


def try_exit():
    if is_closing:
        tornado.ioloop.IOLoop.instance().stop()


argparser = argparse.ArgumentParser(prog='tornadopush',
    description='Start tornadopush server')
argparser.add_argument('-p', '--port', default=8888, type=int,
    help='Port number')
argparser.add_argument('-c', '--config', default='config.yml',
    help='Path to a YAML configuration file')
argparser.add_argument('--debug', default=False, action='store_true',
    help="Enable debug messages")
argparser.add_argument('--auth', default=False, action='store_true',
    help="Whether to make authentification mandatory")
argparser.add_argument('--secret', default='tornadopush',
    help='Secret key for the token serializer')
argparser.add_argument('--tokenttl', default=3600, type=int,
    help='Token duration in seconds')
argparser.add_argument('--default-channel', default='tornado',
    help='Default channel name')
argparser.add_argument('--assets-cache-path',
    help='Path where assets bundles will be compiled')
argparser.add_argument('--queue', default='tornado_redis',
    help='Queue type')
argparser.add_argument('--redis-host', default='localhost',
    help='Redis hostname')
argparser.add_argument('--redis-port', default=6379, type=int,
    help='Redis port')
argparser.add_argument('--publish-method',
    help='If publishing messages to the queue is allowed from tornadopush')
argparser.add_argument('--webhook-url',
    help='A URL to POST data to when a message is received from the client')

def main():
    args = argparser.parse_args()
    settings = {
        "queue": args.queue,
        "token_secret": args.secret,
        "auth_enabled": args.auth,
        "token_max_age": args.tokenttl,
        "default_channel": args.default_channel,
        "cache_path": args.assets_cache_path,
        "redis_host": args.redis_host,
        "redis_port": args.redis_port,
        "publish_method": args.publish_method,
        "webhook_url": args.webhook_url,
        "debug": args.debug
    }
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if os.path.exists(args.config):
        with open(args.config) as f:
            settings.update(yaml.load(f.read()))
    print "Starting tornadopush on port %s" % args.port
    print "Press Ctrl+C to exit"
    signal.signal(signal.SIGINT, signal_handler)
    tornado.ioloop.PeriodicCallback(try_exit, 100).start()
    start_server(args.port, **settings)


if __name__ == '__main__':
    main()