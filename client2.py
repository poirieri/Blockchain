import paho.mqtt.client as mqtt

PUB_KEYS_TOPIC = "PubKeys"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(PUB_KEYS_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    addPubKey(msg.payload)

def on_message_callback(client, sub, callback):
    print(callback)

class Publickey:
    def __init__(self, id, key):
        self.id = id
        self.key = key

def addPubKey(key):
    first = Publickey(1, key)
    print(first.key)

def pump_callback(client, userdata, message):
    #print("Received message '" + str(message.payload) + "' on topic '"
    #    + message.topic + "' with QoS " + str(message.qos))
    print(message.payload)
    # Things.set_waterPumpSpeed(int())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
# client.loop_start()
client.message_callback_add(PUB_KEYS_TOPIC, pump_callback)
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

