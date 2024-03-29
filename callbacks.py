import json
import logging
import time
from bson import BSON
from helpers import utils
import data_collector, Block
from dbconf import add_to_db
import global_variables as gl
import helpers.common_topics as ct

MINIMUM_TRANSACTIONS = int(gl.minimum_nodes/2)
MINIMUM_NODES = gl.minimum_nodes


def add_new_block(client, userdata, message):
    """Callback for NEW_BLOCK
        Takes place when a piece of data is sent to other devices to become a part of currently mined block
        It appends to a list temporary_blocks and when a specific number of blocks are received, miner can start validating
        each of them.
        message.payload = {
                            "id": str,
                            "mac": str,
                            "signature": byte,
                            "transactions": [list],
                            "time": str(datetime.datetime.utcnow())
                            """
    if not gl.is_miner:
        received_block = json.loads(message.payload)
        timestamp = received_block.pop("time")
        computed_block = []
        try:
            if gl.block_chain.blocks.__len__() == 0 and not gl.is_miner:
                computed_block = Block.Chain.get_first_block(timestamp,
                                                             received_block)
                gl.block_chain.blocks.append(computed_block)
            elif gl.block_chain.blocks.__len__() != 0 and not gl.is_miner:
                gl.block_chain.add_block(timestamp,
                                         received_block)
                computed_block = gl.block_chain.blocks[-1]
            logging.info("New block mined!\n")

        except KeyError:
            logging.error("Error in add_new_block()")
        for i in computed_block.data:
            gl.temporary_blocks = list(filter(lambda x: json.loads(x['transactions']) != computed_block.data[i]['transactions'],
                       gl.temporary_blocks))
        del computed_block
    gl.is_mining = False
    if gl.is_miner:
        utils.choose_new_miner(client)


def receive_and_send_encrypted_block(client, userdata, message):
    """Callback for SEND_ENCRYPTED_MESSAGE
    Takes place when a piece of data is sent to other devices to become a part of currently mined block
    It appends to a list temporary_blocks and when a specific number of blocks are received, miner can start validating
    each of them. After validation miner publishes new block.
    message.payload = {
                        "id": str,
                        "mac": str,
                        "signature": byte,
                        "transactions": [list]
                        }
                        """
    received_encrypted_block = json.loads(message.payload)
    gl.temporary_blocks.append(received_encrypted_block)
    if gl.temporary_blocks.__len__() >= MINIMUM_TRANSACTIONS and gl.is_miner:
        try:
            validated_block = utils.validate_blocks(client, gl.temporary_blocks)
            if gl.is_miner:  # to be commented
                comp_block = validated_block.copy()
                timestamp = comp_block.pop('time')
                for i in comp_block:
                    comp_block[i]['transactions'] = json.loads(comp_block[i]['transactions'])
                try:
                    computed_block = []
                    if gl.block_chain.blocks.__len__() == 0:
                        computed_block = Block.Chain.get_first_block(timestamp,
                                                                     comp_block)
                        gl.block_chain.blocks.append(computed_block)
                    else:
                        gl.block_chain.add_block(timestamp,
                                                 comp_block)
                        computed_block = gl.block_chain.blocks[-1]
                    logging.info("New block mined!\n")
                except KeyError:
                    logging.error("Error in add_new_block()")
                add_to_db(computed_block)
                client.publish(ct.NEW_BLOCK, json.dumps(validated_block), qos=2)
        except KeyError:
            logging.debug("Error in receive_encrypted_block()")


def add_trust_rate_to_store(client, userdata, message):
    """Callback for RESPOND_WITH_OWN_TRUST_RATE
    Takes place when a message with trust rate value is received from other device.
    Adds to dictionary trust rate and sends current trust rate for device.
    message.payload = {id_device : trust_rate}
        """
    try:
        new_device_trust_rate = json.loads(message.payload)
        gl.trusted_devices.update(new_device_trust_rate)
    except KeyError:
        logging.error("Error in add_trust_rate_to_store()")


def increment_trust_value(client, userdata, message):
    """Callback for CORRECT_VALIDATION
    message.payload - device_id of device with good behaviour
    It searches for device_id in trusted deviced dictionary and increments it by 1
    """
    id_good_device = str(message.payload, "UTF-8")
    try:
        trust_value = 20 if (gl.trusted_devices.get(id_good_device) + 1) >= 20 else \
            (gl.trusted_devices.get(id_good_device) + 1)
        gl.trusted_devices.update({id_good_device: trust_value})
        logging.info("Trust rate updated: " + str({id_good_device: trust_value}))
    except TypeError:
        logging.error("Error in add_trust_value()")


def decrement_trust_value(client, userdata, message):
    """Callback for FALSE_VALIDATION
    message.payload - device_id of device with bad behaviour
    It searches for device_id in trusted deviced dictionary and decrements it by 2
    """
    id_bad_device = str(message.payload, "UTF-8")
    try:
        trust_value = 0 if (gl.trusted_devices.get(id_bad_device) - 2) < 0 else \
            (gl.trusted_devices.get(id_bad_device) - 2)
        gl.trusted_devices.update({id_bad_device: trust_value})
        logging.info("Trust rate updated: " + str({id_bad_device: trust_value}))
    except TypeError:
        logging.error("Error in decrement_trust_value()")


def new_miner_status(client, userdata, message):
    """Callback for CHOOSE_MINER
    message.payload - device_id of chosen new miner for next block
    """
    try:
        gl.is_miner = True if str(message.payload, "UTF-8") == userdata.get("id_device") else False
        if gl.trusted_devices.__len__() >= MINIMUM_NODES and gl.list_devices.__len__() >= MINIMUM_NODES and gl.is_miner:
            client.publish(ct.START_COLLECTING, qos=2)
            logging.info("Start collecting data for new block - miner")
    except KeyError:
        logging.debug("Error in new_miner_status()")


def add_device_info_to_store(client, userdata, message):
    """Callback for NEW_DEVICE_INFO
    Takes place after other device adds device info about one's device and send their's.
    Adds to list of devices.
    message.payload = {id: ...,
                        mac_address: ...,
                        client/id_device: ...,
                        public_key_e: ...,
                        public_key_n: ...
                        }
    """
    try:
        new_device_info = json.loads(message.payload)
        utils.update_list_devices(new_device_info)
    except KeyError:
        logging.error("Error in add_device_info_to_store()")


def receive_and_send_device_info(client, userdata, message):
    """Callback for NEW_DEVICE_INFO_RESPOND
    Takes place when a message with device info is received from other device.
    Adds to list of devices and sends information about own device.
    message.payload = {id: ...,
                        mac_address: ...,
                        client/id_device: ...,
                        public_key_e: ...,
                        public_key_n: ...
                        }
    """
    try:
        received_device_info = json.loads(message.payload)
        if received_device_info['id'] != userdata.get('id_device'):
            utils.update_list_devices(received_device_info)
            # logging.info("Updated device list with: " + received_device_info.__repr__() + "\n")
            logging.debug("Device list: " + str(gl.list_devices))
            client.publish(ct.NEW_DEVICE_INFO, json.dumps(gl.list_devices[0].__dict__))
    except KeyError:
        logging.error("receive_and_send_device_info() - Error")


def receive_and_send_trust_rate(client, userdata, message):
    """Callback for NEW_DEVICE_TRUST_RATE
    Takes place when a message with trust rate value is received from other device.
    Adds to dictionary trust rate and sends current trust rate for device.
    message.payload = {id_device : trust_rate}
    """
    received_trust_rate = json.loads(message.payload)
    try:
        gl.trusted_devices.update(received_trust_rate)
        logging.info("Updated trust list with: " + str(received_trust_rate) + "\n")
        logging.debug("Current trust list: " + str(gl.trusted_devices))

        own_trust_rate = {
            userdata.get("id_device"): gl.trusted_devices.get(userdata.get("id_device"))
        }
        client.publish(ct.RESPOND_WITH_OWN_TRUST_RATE, json.dumps(own_trust_rate), qos=2)
        if gl.trusted_devices.__len__() >= MINIMUM_NODES and gl.list_devices.__len__() >= MINIMUM_NODES and gl.is_miner:
            client.publish(ct.START_COLLECTING, qos=2)
    except KeyError:
        logging.error("Error in receive_and_send_trust_rate()")


def delete_device(client, userdata, message):
    """Callback for Last will message - DEVICE_OFFLINE
    Takes care of removing information about device
    message.payload = device_id
    """
    inactive_device_id = str(message.payload, "UTF-8")
    try:
        gl.list_devices = list(filter(lambda x: x.id != inactive_device_id, gl.list_devices))
        gl.trusted_devices.pop(inactive_device_id)
        logging.info("Device inactive: " + inactive_device_id.__str__() + "\n")
        logging.debug("Devices active: " + str(gl.list_devices) + "\n" +
                      "Trust list" + str(gl.trusted_devices))
    except KeyError:
        logging.error("Error in delete_device() - no device detected")
