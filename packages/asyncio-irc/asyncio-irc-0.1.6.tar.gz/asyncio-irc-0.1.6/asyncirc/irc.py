import asyncio
import base64
import functools
import importlib
import logging
import socket
import ssl
from blinker import signal
from .parser import RFC1459Message
loop = asyncio.get_event_loop()

plugins = []
def plugin_registered_handler(plugin_name):
    logging.getLogger("asyncirc.plugins").info("Plugin {} registered".format(plugin_name))
    plugins.append(plugin_name)

signal("plugin-registered").connect(plugin_registered_handler)

def load_plugins(*plugins):
    for plugin in plugins:
        if plugin not in plugins:
            importlib.import_module(plugin)

class User:
    def __init__(self, nick, user, host):
        self.nick = nick
        self.user = user
        self.host = host

    @classmethod
    def from_hostmask(self, hostmask):
        if "!" in hostmask and "@" in hostmask:
            nick, userhost = hostmask.split("!", maxsplit=1)
            user, host = userhost.split("@", maxsplit=1)
            return self(nick, user, host)
        return self(None, None, hostmask)

class IRCProtocol(asyncio.Protocol):

    ## Required by asyncio.Protocol

    def connection_made(self, transport):
        self.transport = transport
        self.logger = logging.getLogger("asyncirc.IRCProtocol")
        self.buf = ""
        self.nickname = ""

        signal("connected").send(self)

        self.logger.info("Connection success.")
        self.attach_default_listeners()

    def data_received(self, data):
        self.logger.debug("data_received called")
        data = data.decode()
        self.logger.debug("Received: \"{}\"".format(data))

        self.buf += data
        while "\n" in self.buf:
            index = self.buf.index("\n")
            line_received = self.buf[:index].strip()
            self.buf = self.buf[index + 1:]
            self.logger.debug("Line received: \"{}\"".format(line_received))
            message = RFC1459Message.from_message(line_received)
            message.client = self
            signal("irc").send(message)
            signal("irc-{}".format(message.verb.lower())).send(message)

    def connection_lost(self, exc):
        self.logger.info("Connection lost; stopping event loop.")
        loop.stop()

    ## Core helper functions

    def on(self, event):
        def process(f):
            self.logger.debug("Registering function for event {}".format(event))
            signal(event).connect(f)
            return f
        return process

    def writeln(self, line):
        if not isinstance(line, bytes):
            line = line.encode()
        self.transport.get_extra_info('socket').send(line + b"\r\n")
        signal("irc-send").send(line.decode())

    def register(self, nick, user, realname, mode="+i", password=None):
        if password:
            self.writeln("PASS {}".format(password))
        self.writeln("USER {0} {1} {0} :{2}".format(user, mode, realname))
        self.writeln("NICK {}".format(nick))
        self.nickname = nick

    ## Default listeners

    def attach_default_listeners(self):
        signal("irc-ping").connect(_pong)
        signal("irc-privmsg").connect(_redispatch_privmsg)
        signal("irc-notice").connect(_redispatch_notice)
        signal("irc-join").connect(_redispatch_join)
        signal("irc-part").connect(_redispatch_part)
        signal("irc-quit").connect(_redispatch_quit)
        signal("irc-kick").connect(_redispatch_kick)
        signal("irc-nick").connect(_redispatch_nick)

    ## protocol abstractions

    def join(self, channels):
        if not isinstance(channels, list):
            channels = [channels]
        channels_str = ",".join(channels)
        self.writeln("JOIN {}".format(channels_str))

    def part(self, channels):
        if not isinstance(channels, list):
            channels = [channels]
        channels_str = ",".join(channels)
        self.writeln("PART {}".format(channels_str))

    def say(self, target_str, message):
        while message:
            self.writeln("PRIVMSG {} :{}".format(target_str, message[:400]))
            message = message[400:]

## for redefining (i.e. channel-tracking mechanism)

def get_user(hostmask):
    if "!" not in hostmask or "@" not in hostmask:
        return hostmask
    return User.from_hostmask(hostmask)

def get_channel(channel):
    return channel

def get_target(x):
    return x

## default listener functions

def _pong(message):
    message.client.logger.debug("Responding to PING")
    message.client.writeln("PONG {}".format(message.params[0]))

def _redispatch_message_common(message, type):
    target, text = get_target(message.params[0]), message.params[1]
    user = get_user(message.source)
    signal(type).send(message, user=user, target=target, text=text)
    if target == message.client.nickname:
        signal("private-{}".format(type)).send(message, user=user, target=target, text=text)
    else:
        signal("public-{}".format(type)).send(message, user=user, target=target, text=text)

def _redispatch_privmsg(message):
    message.client.logger.debug("Redispatching PRIVMSG {}".format(message))
    _redispatch_message_common(message, "message")

def _redispatch_notice(message):
    message.client.logger.debug("Redispatching NOTICE {}".format(message))
    _redispatch_message_common(message, "notice")

def _redispatch_join(message):
    message.client.logger.debug("Redispatching JOIN {}".format(message))
    user = get_user(message.source)
    channel = get_channel(message.params[0])
    signal("join").send(message, user=user, channel=channel)

def _redispatch_part(message):
    message.client.logger.debug("Redispatching PART {}".format(message))
    user = get_user(message.source)
    channel, reason = get_channel(message.params[0]), None
    if len(message.params) > 1:
        reason = message.params[1]
    signal("part").send(message, user=user, channel=channel, reason=reason)

def _redispatch_quit(message):
    message.client.logger.debug("Redispatching QUIT {}".format(message))
    user = get_user(message.source)
    reason = message.params[0]
    signal("quit").send(message, user=user, reason=reason)

def _redispatch_kick(message):
    message.client.logger.debug("Redispatching KICK {}".format(message))
    kicker = get_user(message.source)
    channel, kickee, reason = get_channel(message.params[0]), get_user(message.params[1]), message.params[2]
    signal("kick").send(message, kicker=kicker, kickee=kickee, channel=channel, reason=reason)

def _redispatch_nick(message):
    message.client.logger.debug("Redispatching NICK {}".format(message))
    old_user = get_user(message.source)
    new_nick = message.params[0]
    signal("nick").send(message, user=old_user, new_nick=new_nick)

## public functional API

def connect(server, port=6697, use_ssl=True):
    connector = loop.create_connection(IRCProtocol, host=server, port=port, ssl=use_ssl)
    transport, protocol = loop.run_until_complete(connector)
    return protocol
