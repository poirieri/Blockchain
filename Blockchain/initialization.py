import json
import logging
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import Blockchain.helpers.utils as utils
import Blockchain.global_variables as gl
import Blockchain.helpers.common_topics as ct


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
                          "mac_address": mac_address,
                          "priv_key": keys[1],
                          })
    client.on_connect = utils.on_connect
    client.will_set(ct.DEVICE_OFFLINE, payload=id_device, qos=0, retain=True)
    client.on_message = utils.on_message
    client.connect(gl.host, gl.port, keepalive=60)
    return client


def prepare_device_info(keys, id_device, mac_address):
    topic = ct.CLIENT + str(id_device)
    device_info = DeviceInfo(id_device, mac_address, topic, keys[0]['e'], keys[0]['n'])
    return device_info


def send_device_info(keys, device_id, mac_address, trust_rate):
    try:
        device_info = prepare_device_info(keys, device_id, mac_address)
        json_device_info = json.dumps(device_info.__dict__)
        gl.list_devices.append(device_info)
        logging.debug("Current list of devices: " + gl.list_devices.__repr__())
        device_trust_rate = {str(device_id): trust_rate}
        gl.trusted_devices.update(device_trust_rate)
        msgs = [(ct.NEW_DEVICE_INFO_RESPOND, json_device_info, 2, True),
                (ct.NEW_DEVICE_TRUST_RATE, json.dumps(device_trust_rate), 2, True)]

        publish.multiple(msgs)

    except ConnectionError:
        logging.error(ConnectionError, "Error send_device_info()")



