import json
import uuid
import bson
import paho.mqtt.client as mqtt
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


def configure_client(id_device, is_miner, mac_address, keys):
    client = mqtt.Client()
    client.user_data_set({"id_device": id_device,
                          "isMiner": is_miner,
                          "mac_address": mac_address,
                          "pub_key": keys[0],
                          "priv_key": keys[1],
                          })
    client.will_set(helpers.utils.DEVICE_OFFLINE, payload=id_device, qos=0, retain=True)
    client.on_connect = helpers.utils.on_connect
    client.on_message = helpers.utils.on_message
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
        main.list_devices.append(prepare_device_info(keys, device_id, mac_address))
        client.publish(helpers.utils.NEW_DEVICE_INFO_RESPOND, json_string)
        main.trusted_devices.update({str(device_id) : trust_rate})
        send_trust_rate(client, device_id, trust_rate)
    except ConnectionError:
        print(ConnectionError)


def send_trust_rate(client, device_id,  trust_rate):
    client.publish(helpers.utils.NEW_DEVICE_TRUST_RATE, json.dumps({str(device_id): trust_rate}))


def send_block(client, block):
    try:
        client.publish(helpers.utils.SEND_ENCRYPTED_MESSAGE, block)
    except ConnectionError:
        print(ConnectionError)



