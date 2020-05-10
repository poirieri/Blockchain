import json
import logging
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from bson import BSON

from Blockchain import security
import Blockchain.helpers.utils
import Blockchain.global_variables as gl


class DeviceInfo:
    def __init__(self, id_device, mac_address, topic, public_key_e, public_key_n):
        self.id = id_device
        self.mac_address = mac_address
        self.topic = topic
        self.public_key_e = public_key_e
        self.public_key_n = public_key_n

    def __repr__(self) -> str:
        return "ID: " + self.id + ", mac address: " + self.mac_address + " ;"


def configure_client(id_device, is_miner, mac_address, keys):
    client = mqtt.Client(clean_session=True)
    client.user_data_set({"id_device": id_device,
                          "isMiner": is_miner,
                          "mac_address": mac_address,
                          "pub_key": keys[0],
                          "priv_key": keys[1],
                          })
    client.on_connect = Blockchain.helpers.utils.on_connect
    client.will_set(Blockchain.helpers.utils.DEVICE_OFFLINE, payload=id_device, qos=0, retain=True)
    client.on_message = Blockchain.helpers.utils.on_message
    client.connect("localhost", 1883, 60)

    return client


def configure_keys():
    keys = security.generate_keys()
    return keys


def prepare_device_info(keys, id_device, mac_address):
    topic = "client/" + str(id_device)
    device_info = DeviceInfo(id_device, mac_address, topic, keys[0]['e'], keys[0]['n'])
    return device_info


def send_device_info(client, keys, device_id, mac_address, trust_rate):
    try:
        json_string = json.dumps(prepare_device_info(keys, device_id, mac_address).__dict__)
        gl.list_devices.append(prepare_device_info(keys, device_id, mac_address))
        logging.debug("Current list of devices: " + gl.list_devices.__repr__())
        gl.trusted_devices.update({str(device_id): trust_rate})
        msgs = [(Blockchain.helpers.utils.NEW_DEVICE_INFO_RESPOND, json_string, 2, True),
                         (Blockchain.helpers.utils.NEW_DEVICE_TRUST_RATE, json.dumps({str(device_id): trust_rate}),
                          2, True)]
        publish.multiple(msgs)

    except ConnectionError:
        logging.debug(ConnectionError + "Error send_device_info()")


def send_block(client, block):
    try:
        logging.debug("data send - send_block()")
        client.publish(Blockchain.helpers.utils.SEND_ENCRYPTED_MESSAGE, block)
    except ConnectionError:
        logging.debug(ConnectionError + "Error send_block")



