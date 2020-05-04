import callbacks
from helpers.common_topics import *

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
    client.subscribe(NEW_DEVICE_INFO)
    client.subscribe(SEND_ENCRYPTED_MESSAGE)
    client.subscribe(RESPOND_WITH_OWN_TRUST_RATE)
    client.subscribe(FALSE_VALIDATION)
    client.subscribe(CORRECT_VALIDATION)
    client.subscribe(NEW_BLOCK)
    client.subscribe(CHOOSE_MINER)
    client.subscribe(NEW_DEVICE_DEVICE_INFO)
    client.subscribe(NEW_DEVICE_TRUST_RATE)
    client.subscribe(DEVICE_OFFLINE)



def add_callbacks(client):
    client.message_callback_add(NEW_BLOCK, callbacks.add_new_block)
    client.message_callback_add(RESPOND_WITH_OWN_TRUST_RATE, callbacks.add_trust_rate_to_store)
    client.message_callback_add(NEW_DEVICE_INFO, callbacks.add_device_info_to_store)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE, callbacks.receive_encrypted_block)
    client.message_callback_add(CORRECT_VALIDATION, callbacks.add_trust_value)
    client.message_callback_add(FALSE_VALIDATION, callbacks.decrement_trust_value)
    client.message_callback_add(NEW_DEVICE_DEVICE_INFO, callbacks.receive_and_send_device_info)
    client.message_callback_add(NEW_DEVICE_TRUST_RATE, callbacks.receive_and_send_trust_rate)
    client.message_callback_add(DEVICE_OFFLINE, callbacks.delete_device)

