import callbacks
from helpers.common_topics import *
import main

def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    print("Connected with result code "+str(rc))
    subscribe_topics(client)
    add_callbacks(client)


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    print(msg.topic+" "+str(msg.payload))


def subscribe_topics(client):
    client.subscribe(PUB_KEYS_TOPIC)
    client.subscribe(SEND_ENCRYPTED_MESSAGE + str(main.id_device))
    client.subscribe(SEND_ENCRYPTED_MESSAGE)
    client.subscribe(TRUST_RATE)
    client.subscribe(NEW_BLOCK)


def add_callbacks(client):
    client.message_callback_add(NEW_BLOCK, callbacks.add_new_block)
    client.message_callback_add(TRUST_RATE, callbacks.add_trust_rate_to_store)
    client.message_callback_add(callbacks.add_device_info_to_store)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE + str(main.id_device), callbacks.decrypt_callback)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE, callbacks.decrypt_callback)