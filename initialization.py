import json
import uuid
# printing the value of unique MAC
# address using uuid and getnode() function
import paho.mqtt.client as mqtt

import security
import helpers.utils
import MinimalBlock
from helpers.common_topics import SEND_ENCRYPTED_MESSAGE, PUB_KEYS_TOPIC
import main


class DeviceInfo():

    def __init__(self, id, mac_address, topic, public_key_e, public_key_n):
        self.id = id
        self.mac_address = mac_address
        self.topic = topic
        self.public_key_e = public_key_e
        self.public_key_n = public_key_n

def configure_client():

    client = mqtt.Client()
    client.on_connect = helpers.utils.on_connect
    client.on_message = helpers.utils.on_message
    client.connect("localhost", 1883, 60)
    client.subscribe(helpers.utils.PUB_KEYS_TOPIC)
    client.subscribe(SEND_ENCRYPTED_MESSAGE + str(main.ID))
    client.subscribe(SEND_ENCRYPTED_MESSAGE)
    client.message_callback_add(PUB_KEYS_TOPIC, MinimalBlock.public_keys_callback)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE + str(main.ID), MinimalBlock.decrypt_callback)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE, MinimalBlock.decrypt_callback)


    return client

def configure_keys(keys):

    if (keys is None):
        keys = security.generate_keys()
        return keys

def prepare_json_to_send(data, ID):
    data_set = {
        "id" : ID,
        "data" : {
           "e" : data[0].e,
            "n" : data[0].n
        }
    }
    return json.dumps(data_set)


def prepare_device_info(keys):
    mac_address = hex(uuid.getnode())
    topic = "client/" + str(main.ID)
    device_info = DeviceInfo(main.ID, mac_address, topic, keys[0]['e'], keys[0]['n'])
    return device_info


def send_keys(client, device_info):
    try:
        json_string = helpers.utils.aBlockEncoder().encode(device_info)
        client.publish(helpers.utils.PUB_KEYS_TOPIC, json_string)
    except ConnectionError:
        pass

def send_block(client, block):
    try:
        # json_string = helpers.utils.aBlockEncoder().encode(block)
        client.publish(helpers.utils.SEND_ENCRYPTED_MESSAGE, block)
    except ConnectionError:
        pass