from jsmin import jsmin
import os

static_path = os.path.join(os.path.dirname(__file__), 'static')
asset_files = ['eventsource.js', 'reconnecting-websocket.js',
    'presence.js', 'push.js']


def generate_bundle(files=None, host=None, root=static_path):
    if not files:
        files = asset_files
    content = ""
    for filename in files:
        with open(os.path.join(root, filename)) as f:
            content += f.read()
    if host:
        content += "tornadopush.init('%s');" % host
    return jsmin(content)


def generate_authentication_code(token):
    return "tornadopush.authentify('%s');" % str(token)


def generate_tokenized_bundle(token, files, **kwargs):
    content = generate_bundle(files, **kwargs)
    content += generate_authentication_code(token)
    return content