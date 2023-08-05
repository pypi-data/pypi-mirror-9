if (typeof(tornadopush) === 'undefined') {
    var tornadopush = {};
}

(function(tp) {

    var debug = function(o) {
        if (tp.DEBUG) {
            console.log(o);
        }
    };
       
    var noop = function() {};

    var PresenceChannel = tp.PresenceChannel = function(name, presence) {
        this.name = name;
        this.presence = presence;
        this.joined = false;
        this.meta = {};
        this.users = {};
        this.onjoin = noop;
        this.onmeta = noop;
        this.onleave = noop;
        this.onusers = noop;
        this.onmessage = noop;
    };

    PresenceChannel.prototype.join = function(meta) {
        if (!this.joined) {
            this.meta = meta || {};
            this.joined = true;
            this._send('join:' + JSON.stringify(this.meta));
            debug('Presence: joined #' + this.name);
        }
    };

    PresenceChannel.prototype.leave = function() {
        this._send('leave:');
        this.joined = false;
        debug('Presence: left #' + this.name);
    };

    PresenceChannel.prototype.handle = function(action, payload) {
        var splitPayload = function() {
            var id = payload.substr(0, payload.indexOf(';'));
            return {id: id, data: payload.substr(id.length + 1)};
        };

        if (action === '+') {
            var data = splitPayload();
            this.users[data.id] = JSON.parse(data.data);
            debug('Presence: user ' + data.id + ' joined #' + this.name);
            this.onjoin(data.id, this.users[data.id]);
        } else if (action === '-') {
            delete this.users[payload];
            debug('Presence: user ' + payload + ' left #' + this.name);
            this.onleave(payload);
        } else if (action === 'users') {
            this.users = JSON.parse(payload);
            debug('Presence: refreshed user list on #' + this.name);
            this.onusers(this.users);
        } else if (action === 'bcast') {
            var data = splitPayload();
            debug('Presence: received broadcast on #' + this.name + ' from ' + data.id + ': ' + data.data);
            this.onmessage(data.id, data.data);
        } else if (action === 'meta') {
            var data = splitPayload();
            this.users[data.id] = JSON.parse(data.data);
            debug('Presence: meta changed for ' + data.id + ' on #' + this.name);
            this.onmeta(data.id, this.users[data.id]);
        }
    };

    PresenceChannel.prototype._send = function(msg) {
        if (!this.joined) {
            throw Error('Cannot use a presence channel which is not joined');
        }
        this.presence._send(this.name + ':' + msg);
    };

    PresenceChannel.prototype.set_meta = function(meta) {
        this.meta = meta;
        this._send_meta();
    };

    PresenceChannel.prototype.set_meta_prop = function(name, value) {
        this.meta[name] = value;
        this._send_meta();
    };

    PresenceChannel.prototype._send_meta = function() {
        this._send('meta:' + JSON.stringify(this.meta));
        debug('Presence: set meta on #' + this.name);
    };

    PresenceChannel.prototype.refresh_users = function() {
        this.users = {};
        this._send('users:');
    };

    PresenceChannel.prototype.user_ids = function() {
        return Object.keys(this.users);
    };

    PresenceChannel.prototype.get_user_meta = function(id) {
        return this.users[id];
    };

    PresenceChannel.prototype.broadcast = function(message) {
        this._send('bcast:' + message);
        debug('Presence: broadcasted on #' + this.name + ': ' + message);
    };


    var Presence = tp.Presence = function(socket, auto_joined_channel) {
        this.socket = null;
        this.channels = {};
        this.msg_prefix = 'presence:';
        this._send_buffer = [];
        this._first_connect = true;
        if (auto_joined_channel) {
            this.channel = new PresenceChannel(auto_joined_channel, this);
            this.channel.joined = true;
            this.channels[auto_joined_channel] = this.channel;
        }
        if (socket) {
            this.listen(socket);
        }
    };

    Presence.from_url = function(url) {
        var ws = ReconnectingWebSocket ? ReconnectingWebSocket : WebSocket;
        return new Presence(new ws(url));
    };

    Presence.prototype.join = function(channel, meta) {
        if (!this.channels[channel]) {
            this.channels[channel] = new PresenceChannel(channel, this);
        }
        this.channels[channel].join(meta);
        return this.channels[channel];
    };

    Presence.prototype.listen = function(socket) {
        this.socket = socket;
        var prev_onmessage = socket.onmessage,
            prev_onopen = socket.onopen,
            self = this;
        socket.onopen = function(e) {
            if (prev_onopen) {
                prev_onopen(e);
            }
            if (!this._first_connect) {
                angular.forEach(this.channels, function(channel) {
                    channel._send_meta();
                });
            }
            self._flush_send_buffer();
            this._first_connect = false;
        };
        socket.onmessage = function(e) {
            if (prev_onmessage) {
                prev_onmessage(e);
            }
            if (e.data.substr(0, 9) === 'presence:') {
                self.handle_message(e.data.substr(9));
            }
        };
    };

    Presence.prototype.handle_message = function(msg) {
        var channel = msg.substr(0, msg.indexOf(':')),
            action = msg.substring(channel.length + 1, msg.indexOf(':', channel.length + 1)),
            payload = msg.substr(channel.length + action.length + 2);
        if (this.channels[channel]) {
            this.channels[channel].handle(action, payload);
        }
    };

    Presence.prototype._send = function(msg) {
        if (!this.socket) {
            throw Error('No sockets for presence broadcast (this can happen if you are using presence through SSE)');
        } else if (this.socket.readyState === WebSocket.CONNECTING) {
            this._send_buffer.push(msg);
        } else if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(this.msg_prefix + msg);
        }
    };

    Presence.prototype._flush_send_buffer = function() {
        for (var i in this._send_buffer) {
            this.socket.send(this.msg_prefix + this._send_buffer[i]);
        }
        this._send_buffer = [];
    };

    Presence.prototype.close = function() {
        this.socket.close();
        this._send_buffer = [];
    };

    tp.presence = function() {
        if (!tp._presence) {
            if (!tp.hostname) {
                tp.init();
            }
            if (!tp.ws_support) {
                throw Error('Presence notification requires WebSocket support');
            }
            tp._presence = tp.Presence.from_url(tp.wsurl('/presence'));
        }
        return tp._presence;
    };

    tp.join = function(channel) {
        return tp.presence().join(channel);
    };

})(tornadopush);