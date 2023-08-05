if (typeof(tornadopush) === 'undefined') {
    var tornadopush = {};
}

(function(tp) {

    tp.DEBUG = false;
    var debug = function(o) {
        if (tp.DEBUG) {
            console.log(o);
        }
    };

    tp.SSEChannelListener = (function() {
        var _ = function(url, presence) {
            this.url = url;
            this.source = new EventSource(url);
            if (presence) {
                this.enable_presence(presence);
            }
        };

        _.prototype.bind = function(event, callback) {
            this.source.addEventListener(event, function(e) {
                debug("Received event: " + event);
                var data = tp.decode_data(e.data);
                callback(data);
            });
        };

        _.prototype.send = function(data) {
            var req = new XMLHttpRequest();
            req.onload = function() {
                debug('Data submitted');
            };
            req.open("POST", this.url, true);
            req.setRequestHeader("Content-Type", "application/json");
            req.send(tp.encode_data(data));
        };

        _.prototype.enable_presence = function(presence) {
            debug("Presence enabled through push channel");
            this.presence = presence;
            var self = this;
            this.source.addEventListener('__presence__', function(e) {
                self.presence.handle_message(e.data);
            });
            return presence;
        };

        _.prototype.close = function() {
            this.source.close();
        };

        return _;
    })();

    tp.WebSocketChannelListener = (function() {
        var _ = function(socket, presence) {
            this.listeners = {};
            this.presence = null;
            this.socket = null;
            if (socket) {
                this.listen(socket);
            }
            if (presence) {
                this.enable_presence(presence);
            }
        };

        _.from_url = function(url, presence) {
            var ws = ReconnectingWebSocket ? ReconnectingWebSocket : WebSocket;
            return new _(new ws(url), presence);
        };

        _.prototype.listen = function(socket) {
            this.socket = socket;
            var self = this;
            var prev_handler = this.socket.onmessage;
            this.socket.onmessage = function(e) {
                if (prev_handler) {
                    prev_handler(e);
                }
                self.message_handler(e);
            };
            if (this.presence) {
                this.presence.listen(this.socket);
            }
        };

        _.prototype.message_handler = function(e) {
            if (e.data.substr(0, 6) !== 'event:') {
                return;
            }
            var evt_data = e.data.substr(6),
                event = evt_data.substr(0, evt_data.indexOf(';')),
                data = evt_data.substr(evt_data.indexOf(';') + 1);
            debug("Received event: " + event);
            data = tp.decode_data(data);
            if (this.listeners[event]) {
                this.listeners[event].forEach(function(cb) {
                    cb(data);
                });
            }
        };

        _.prototype.bind = function(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = [];
            }
            this.listeners[event].push(callback);
        };

        _.prototype.send = function(data) {
            this.socket.send("message:" + tp.encode_data(data));
            debug("Data submitted");
        };

        _.prototype.enable_presence = function(presence) {
            debug("Presence enabled through push channel");
            this.presence = presence;
            if (this.socket) {
                presence.listen(this.socket);
            }
            return presence;
        };

        _.prototype.close = function() {
            this.socket.close();
        };

        return _;
    })();

    tp.init = function (hostname, secured) {
        if (typeof(hostname) === 'undefined' && typeof(TORNADOPUSH_HOSTNAME) !== 'undefined') {
            hostname = TORNADOPUSH_HOSTNAME;
        }
        if (typeof(secured) === 'undefined' && typeof(TORNADOPUSH_SECURED) !== 'undefined') {
            secured = TORNADOPUSH_SECURED;
        }
        tp.hostname = hostname || 'localhost:8888';
        tp.secured = secured || false;
        tp.ws_support = typeof(WebSocket) !== 'undefined';
        if (typeof(TORNADOPUSH_TOKEN) !== 'undefined') {
            tp.authentify(TORNADOPUSH_TOKEN);
        }
    };

    tp.authentify = function(token) {
        tp.auth_token = token;
    };

    tp.url = function(path, scheme) {
        scheme = scheme || (tp.secured ? 'https://' : 'http://');
        var url = scheme + tp.hostname + path;
        if (tp.auth_token) {
            url +=  (path.indexOf('?') > -1 ? '&' : '?')
                 + 'token=' + encodeURIComponent(tp.auth_token);
        }
        return url;
    };

    tp.wsurl = function(path) {
        return tp.url(path, (tp.secured ? 'wss://' : 'ws://'));
    };

    tp.decode_data = function(data) {
        if (!data) {
            return null;
        }
        return JSON.parse(data);
    };

    tp.encode_data = function(data) {
        if (typeof(data) === 'string') {
            return data;
        }
        return JSON.stringify(data);
    }

    tp.endpointurl = function(opts) {
        if (typeof(opts) == 'string') {
            opts = {"channel": opts};
        }
        if (!opts['channel']) {
            throw Error("Missing channel name");
        }
        var qp = '';
        var path = '/channel/' + opts['channel'];
        if (opts['presence'] && typeof(tp.Presence) !== 'undefined') {
            qp = '?presence=1';
        }
        if (opts['sse'] || !tp.ws_support) {
            return tp.url(path + '.sse' + qp);
        }
        return tp.wsurl(path + qp);
    };

    tp.subscribe = function (opts) {
        if (!tp.hostname) {
            tp.init();
        }
        if (typeof(opts) == 'string') {
            opts = {"channel": opts};
        }
        var url = tp.endpointurl(opts);
        var presence = null;
        if (opts['presence']) {
            if (typeof(tp.Presence) === 'undefined') {
                console.error('Presence cannot be enabled through push channel because of missing libs');
            } else {
                presence = new tp.Presence(null, opts['channel']);
            }
        }
        var listener;
        if (opts['sse'] || !tp.ws_support) {
            if (!opts['sse']) {
                console.log('No WebSocket support: fallback to SSE');
            }
            listener = new tp.SSEChannelListener(url, presence);
        } else {
            listener = tp.WebSocketChannelListener.from_url(url, presence);
        }
        listener.channel = opts['channel'];
        return listener;
    };

})(tornadopush);