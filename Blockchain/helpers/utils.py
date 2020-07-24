import datetime
import json
import logging
import random
import time
from random import randint
from rsa import PublicKey
from Blockchain import security, initialization, callbacks, data_collector
import Blockchain.helpers.common_topics as ct
import Blockchain.global_variables as gl
MINIMUM_TRUST_VALUE = 10


def on_connect(client, userdata, flags, rc):
    """ Subscribing in on_connect() means that if we lose the connection and
    reconnect then subscriptions will be renewed.
    """
    logging.debug("Connected with result code "+str(rc))
    if rc == 0:
        subscribe_topics(client)
        add_callbacks(client)


def on_message(client, userdata, msg):
    """ The callback for when a PUBLISH message is received from the server."""
    logging.info(msg.topic)
    if msg.retain == 1:
        logging.debug("This is a retained message")
    if msg.topic == ct.START_COLLECTING and not gl.is_miner and not gl.is_mining:
        gl.is_mining = True
        data_to_send = data_collector.prepare_transactions_block(client,
                                                                 userdata.get("priv_key"),
                                                                 userdata.get("id_device"),
                                                                 userdata.get("mac_address"))
        send_block(client, json.dumps(data_to_send))


def subscribe_topics(client):
    client.subscribe(ct.NEW_DEVICE_INFO, qos=2)
    client.subscribe(ct.NEW_DEVICE_INFO_RESPOND, qos=2)
    client.subscribe(ct.SEND_ENCRYPTED_MESSAGE, qos=2)
    client.subscribe(ct.RESPOND_WITH_OWN_TRUST_RATE, qos=2)
    client.subscribe(ct.FALSE_VALIDATION, qos=2)
    client.subscribe(ct.CORRECT_VALIDATION, qos=2)
    client.subscribe(ct.NEW_BLOCK, qos=2)
    client.subscribe(ct.CHOOSE_MINER, qos=2)
    client.subscribe(ct.NEW_DEVICE_TRUST_RATE, qos=2)
    client.subscribe(ct.DEVICE_OFFLINE, qos=2)
    client.subscribe(ct.START_COLLECTING, qos=2)


def add_callbacks(client):
    client.message_callback_add(ct.NEW_BLOCK, callbacks.add_new_block)
    client.message_callback_add(ct.RESPOND_WITH_OWN_TRUST_RATE, callbacks.add_trust_rate_to_store)
    client.message_callback_add(ct.NEW_DEVICE_INFO, callbacks.add_device_info_to_store)
    client.message_callback_add(ct.SEND_ENCRYPTED_MESSAGE, callbacks.receive_and_send_encrypted_block)
    client.message_callback_add(ct.CORRECT_VALIDATION, callbacks.increment_trust_value)
    client.message_callback_add(ct.FALSE_VALIDATION, callbacks.decrement_trust_value)
    client.message_callback_add(ct.NEW_DEVICE_INFO_RESPOND, callbacks.receive_and_send_device_info)
    client.message_callback_add(ct.NEW_DEVICE_TRUST_RATE, callbacks.receive_and_send_trust_rate)
    client.message_callback_add(ct.DEVICE_OFFLINE, callbacks.delete_device)
    client.message_callback_add(ct.CHOOSE_MINER, callbacks.new_miner_status)


def choose_new_miner(client):
    try:
        could_be_miner = dict(filter(lambda elem: int(elem[1]) >= MINIMUM_TRUST_VALUE, gl.trusted_devices.items()))
        if could_be_miner.__len__() > 1:
            could_be_miner = dict(filter(lambda elem: str(elem[0]) != str(gl.id_device), could_be_miner.items()))
            logging.debug("Devices suitable for mining blocks:" + str(could_be_miner))
        new_miner = random.choice(list(could_be_miner.keys()))
        logging.info("Device chosen to mine next block: " + str(new_miner))
        client.publish(ct.CHOOSE_MINER, new_miner, qos=2)
    except KeyError:
        pass
    except IndexError:
        logging.error("choose_new_miner() - not having anyone who can mine next block")
        new_miner = gl.id_device
        client.publish(ct.CHOOSE_MINER, new_miner, qos=2)


def update_list_devices(new_device_info):
    if list(filter(lambda x: x.id == new_device_info['id'], gl.list_devices)).__len__() == 0:
        gl.list_devices.append(
            initialization.DeviceInfo(new_device_info['id'], new_device_info['mac_address'],
                                      new_device_info['public_key_e'], new_device_info['public_key_n']))
        logging.info("List device updated: " + str(new_device_info['id']))


def find_device_public_key(id_device):
    try:
        filter_obj = list(filter(lambda x: x.id == id_device, gl.list_devices))
        return PublicKey(filter_obj[0].public_key_n, filter_obj[0].public_key_e)
    except IndexError:
        logging.error("find_device_public_key() - Index out of range")


def find_mac_address(id_device):
    try:
        filter_obj = list(filter(lambda x: x.id == id_device, gl.list_devices))
        return filter_obj[0].mac_address
    except IndexError:
        logging.error("find_mac_address() - Index out of range")


def validate_blocks(client, validated_blocks):
    iterator = 0
    new_block = dict()
    for i in validated_blocks:
        try:
            decrypted_message_verification = security.verify_message((i['transactions']).encode(),
                                                                 i['signature'].encode(encoding='latin1'),
                                                                 find_device_public_key(i['id']))
            if find_mac_address(i['id']) == i['mac'] and decrypted_message_verification:
                new_block.update({str(iterator): i})
                iterator += 1
                client.publish(ct.CORRECT_VALIDATION, i['id'], qos=2)
            else:
                client.publish(ct.FALSE_VALIDATION, i['id'], qos=2)
                logging.debug("Fake block: " + i['id'])
        except KeyError:
            client.publish(ct.FALSE_VALIDATION, i['id'], qos=2)
            logging.error("Fake signature: " + i['id'])
        except AttributeError:
            logging.error("validate_blocks() - No public key", i)
            client.publish(ct.NEW_DEVICE_INFO, json.dumps(gl.list_devices[0].__dict__))
    validated_blocks.clear()
    new_block.update({"time": str(datetime.datetime.now())[:19]})
    return new_block


def send_block(client, block):
    try:
        client.publish(ct.SEND_ENCRYPTED_MESSAGE, block)
        logging.debug("Data package send")
    except ConnectionError:
        logging.error(ConnectionError, "Error send_block()")
