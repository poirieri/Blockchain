import json
import uuid
import bson
import paho.mqtt.client as mqtt
import callbacks
import security
import helpers.utils
import main


class DeviceInfo:
    def __init__(self, id_device, mac_address, topic, public_key_e, public_key_n):
        self.id = id_device
        self.mac_address = mac_address
        self.topic = topic
        self.public_key_e = public_key_e
        self.public_key_n = public_key_n


def configure_client():
    client = mqtt.Client()
    client.on_connect = helpers.utils.on_connect
    client.on_message = helpers.utils.on_message
    client.connect("localhost", 1883, 60)
    verify_master_rights(client, main.trust_rate)
    return client


def configure_keys():
    keys = security.generate_keys()
    return keys


def prepare_device_info(keys, ID, mac_address):
    topic = "client/" + str(main.ID)
    device_info = DeviceInfo(main.ID, mac_address, topic, keys[0]['e'], keys[0]['n'])
    return device_info


def send_device_info(client, keys, id, mac_address):
    try:
        json_string = json.dumps(prepare_device_info(keys, id, mac_address).__dict__)
        client.publish(helpers.utils.PUB_KEYS_TOPIC, json_string)
        send_trust_rate(client, main.trust_rate)
    except ConnectionError:
        print(ConnectionError)


def send_trust_rate(client, trust_rate):
    client.publish(helpers.utils.TRUST_RATE, json.dumps({str(main.ID): trust_rate}))


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
