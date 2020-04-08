import json
from json import JSONEncoder

from helpers.common_topics import *
import initialization


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("test")
    client.subscribe(TEST)
    client.subscribe(PUB_KEYS_TOPIC)
    # client.subscribe(SEND_ENCRYPTED_MESSAGE + str(ID))
    client.subscribe(SEND_ENCRYPTED_MESSAGE)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
## Simple blockchain implementation


class aBlockEncoder(JSONEncoder):

    def default(self, object):
        if isinstance(object, initialization.DeviceInfo):
            return object.__dict__

        else:
            return json.JSONEncoder.default(self, object)

class bBlockEncoder(JSONEncoder):

    def default(self, object):
        if isinstance(object, initialization.Block):
            return object.__dict__

        else:
            return json.JSONEncoder.default(self, object)