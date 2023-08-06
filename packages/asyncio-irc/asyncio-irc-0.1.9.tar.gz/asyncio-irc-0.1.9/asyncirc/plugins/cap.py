import asyncirc
import asyncirc.irc
from blinker import signal

cap = signal("irc-cap")
@cap.connect
def handle_cap(message):
    if message.params[1].lower() == "nak":
        return signal("cap-failed").send(message.params[2])
    if message.params[1].lower() == "ack":
        return signal("cap-success").send(message.params[2])

try_cap = signal("send-cap")
@try_cap.connect
def try_cap(cap_name):
    signal("send-raw").send("CAP REQ :{}".format(cap_name))

signal("plugin-registered").send("asyncirc.plugins.cap")
