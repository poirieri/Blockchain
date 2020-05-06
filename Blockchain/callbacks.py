import json
from time import sleep
from bson import BSON
import Blockchain.helpers.utils as utils
from Blockchain import data_collector, MinimalBlock
from Blockchain.dbconf import add_to_db
import Blockchain.global_variables as gl

MAX_BLOCKS = 2

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
    received_block = BSON.decode(message.payload)
    timestamp = received_block.pop("time")
    if gl.block_chain.blocks.__len__() == 0:
        computed_block = MinimalBlock.MinimalChain.get_genesis_block(gl.block_chain,
                                                                     timestamp,
                                                                     received_block)
        gl.block_chain.blocks.append(computed_block)
    else:
        gl.block_chain.add_block(timestamp,
                                 received_block)
        computed_block = gl.block_chain.blocks[-1]
    print("New block mined!\n", computed_block)
    if gl.is_miner is True:  # to be commented
        add_to_db(computed_block)
    del computed_block
    sleep(1)  # to be commented
    data_collector.prepare_transactions_block(client,
                                              userdata.get("priv_key"),
                                              userdata.get("id_device"),
                                              userdata.get("mac_address"))


def receive_encrypted_block(client, userdata, message):
    """Callback for SEND_ENCRYPTED_MESSAGE
    Takes place when a piece of data is sent to other devices to become a part of currently mined block
    It appends to a list temporary_blocks and when a specific number of blocks are received, miner can start validating
    each of them.
    message.payload = {
                        "id": str,
                        "mac": str,
                        "signature": byte,
                        "transactions": [list]
                        }
                        """
    received_encrypted_block = BSON.decode(message.payload)
    gl.temporary_blocks.append(received_encrypted_block)
    if gl.temporary_blocks.__len__() == MAX_BLOCKS and gl.is_miner is True:
        try:
            utils.validate_blocks(client, gl.temporary_blocks)
            gl.temporary_blocks.clear()
            utils.choose_new_miner(client)
        except KeyError:
            pass


def add_trust_rate_to_store(client, userdata, message):
    """Callback for RESPOND_WITH_OWN_TRUST_RATE
    Takes place when a message with trust rate value is received from other device.
    Adds to dictionary trust rate and sends current trust rate for device.
    message.payload = {id_device : trust_rate}
        """
    new_device_trust_rate = json.loads(message.payload)
    gl.trusted_devices.update(new_device_trust_rate)


def add_trust_value(client, userdata, message):
    """Callback for CORRECT_VALIDATION
    message.payload - device_id of device with good behaviour
    It searches for device_id in trusted deviced dictionary and increments it by 1
    """
    id_good_device = str(message.payload, "UTF-8")
    try:
        trust_value = gl.trusted_devices.get(id_good_device) + 1
        if trust_value >= 20:
            trust_value = 20
        gl.trusted_devices.update({id_good_device: trust_value})
    except TypeError:
        None


def decrement_trust_value(client, userdata, message):
    """Callback for FALSE_VALIDATION
    message.payload - device_id of device with bad behaviour
    It searches for device_id in trusted deviced dictionary and decrements it by 2
    """
    id_bad_device = str(message.payload, "UTF-8")
    try:
        trust_value = gl.trusted_devices.get(id_bad_device) - 2
        if trust_value < 0:
            trust_value = 0
        gl.trusted_devices.update({id_bad_device: trust_value})
    except TypeError:
        None


def new_miner_status(client, userdata, message):
    """Callback for CHOOSE_MINER
    message.payload - device_id of chosen new miner for next block
    """
    if str(message.payload, "UTF-8") == userdata.get("id_device"):
        gl.is_miner = True
    else:
        gl.is_miner = False


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
    new_device_info = json.loads(message.payload)
    utils.update_list_devices(new_device_info)

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
        utils.update_list_devices(received_device_info)
        client.publish(utils.NEW_DEVICE_INFO, json.dumps(gl.list_devices[0].__dict__))
    except KeyError:
        pass


def receive_and_send_trust_rate(client, userdata, message):
    """Callback for NEW_DEVICE_TRUST_RATE
    Takes place when a message with trust rate value is received from other device.
    Adds to dictionary trust rate and sends current trust rate for device.
    message.payload = {id_device : trust_rate}
    """
    received_trust_rate = json.loads(message.payload)
    try:
        gl.trusted_devices.update(received_trust_rate)
        client.publish(utils.RESPOND_WITH_OWN_TRUST_RATE,
                       json.dumps({userdata.get("id_device"): int(
                           gl.trusted_devices.get(userdata.get("id_device")))}))
    except KeyError:
        pass


def delete_device(client, userdata, message):
    """Callback for Last will message - DEVICE_OFFLINE
    Takes care of removing information about device
    message.payload = device_id
    """
    inactive_device_id = str(message.payload, "UTF-8")
    try:
        gl.list_devices = list(filter(lambda x: x.id != inactive_device_id, gl.list_devices))
        gl.trusted_devices.pop(inactive_device_id)
        print(inactive_device_id)
    except KeyError:
        pass
