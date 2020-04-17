import json
import uuid

import bson
import paho.mqtt.client as mqtt
import callbacks
import security
import helpers.utils
from helpers.common_topics import SEND_ENCRYPTED_MESSAGE, PUB_KEYS_TOPIC
import main
from bson import BSON

class DeviceInfo:
    def __init__(self, id_device, mac_address, topic, public_key_e, public_key_n):
        self.id = id_device
        self.mac_address = mac_address
        self.topic = topic
        self.public_key_e = public_key_e
        self.public_key_n = public_key_n


class Block:
    def __init__(self, id_device, signature, transactions):
        self.id = id_device
        self.signature = signature
        self.transactions = transactions


def configure_client():
    client = mqtt.Client()
    client.on_connect = helpers.utils.on_connect
    client.on_message = helpers.utils.on_message
    client.connect("localhost", 1883, 60)
    client.subscribe(helpers.utils.PUB_KEYS_TOPIC)
    client.subscribe(SEND_ENCRYPTED_MESSAGE + str(main.ID))
    client.subscribe(SEND_ENCRYPTED_MESSAGE)
    client.subscribe(helpers.utils.TRUST_RATE)
    client.subscribe(helpers.utils.NEW_BLOCK)
    client.message_callback_add(helpers.utils.NEW_BLOCK, callbacks.add_new_block)
    client.message_callback_add(helpers.utils.TRUST_RATE, callbacks.add_trust_rate)
    client.message_callback_add(PUB_KEYS_TOPIC, callbacks.public_keys_callback)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE + str(main.ID), callbacks.decrypt_callback)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE, callbacks.decrypt_callback)
    verify_master_rights(client, main.trust_rate)
    return client


def configure_keys():
    keys = security.generate_keys()
    return keys


def prepare_json_to_send(data, id_device):
    data_set = {
        "id": id_device,
        "data": {
            "e": data[0].e,
            "n": data[0].n
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
        json_string = helpers.utils.DeviceBlockEncoder().encode(device_info)
        client.publish(helpers.utils.PUB_KEYS_TOPIC, json_string)
    except ConnectionError:
        print(ConnectionError)


def send_trust_rate(client, trust_rate):
    client.publish(helpers.utils.TRUST_RATE, bson.encode({str(main.ID): trust_rate}))

def send_block(client, block):
    try:
        client.publish(helpers.utils.SEND_ENCRYPTED_MESSAGE, block)
    except ConnectionError:
        print(ConnectionError)


def verify_master_rights(client, trust_value):
    if trust_value >= 10:
        client.subscribe(helpers.utils.CHECK_BLOCK)
        client.message_callback_add(helpers.utils.CHECK_BLOCK, callbacks.choose_trusted_device)
    else:
        client.unsubscribe(helpers.utils.CHECK_BLOCK)
        client.message_callback_remove(helpers.utils.CHECK_BLOCK)
