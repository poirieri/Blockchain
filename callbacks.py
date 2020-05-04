import datetime
import json
import random
from time import sleep

from rsa import PublicKey
import MinimalBlock
import dbconf
import initialization
import security
from bson import BSON
import helpers.utils
import main
import data_collector
MAX_BLOCKS = 3


def add_device_info_to_store(client, userdata, message):
    tmp_object = json.loads(message.payload)
    if list(filter(lambda x: x.id == tmp_object['id'], main.list_devices)).__len__() == 0:
        main.list_devices.append(
            initialization.DeviceInfo(tmp_object['id'], tmp_object['mac_address'], "client/" + str(tmp_object['id']),
                                  tmp_object['public_key_e'], tmp_object['public_key_n']))


def add_trust_rate_to_store(client, userdata, message):
    temp = json.loads(message.payload)
    main.trusted_devices.update(temp)


def find_device_public_key(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, main.list_devices))
    return PublicKey(filter_obj[0].public_key_n, filter_obj[0].public_key_e)


def delete_device_from_storages(id_device):
    filter_obj = list(filter(lambda x: x.id != id_device, main.list_devices))
    main.list_devices = filter_obj

def find_mac_address(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, main.list_devices))
    return filter_obj[0].mac_address


def receive_encrypted_block(client, userdata, message):
    kubus = BSON.decode(message.payload)
    main.temporary_blocks.append(kubus)
    if main.temporary_blocks.__len__() == MAX_BLOCKS and main.is_miner is True:
        validate_blocks(client, main.temporary_blocks)
        main.temporary_blocks.clear()
        choose_new_miner(client, userdata)


def validate_blocks(client, validated_blocks):
    iterator = 0
    new_block = dict()
    for i in validated_blocks:
        decrypted_message_verification = security.verify_message(i['transactions'].encode(),
                                                                 i['signature'],
                                                                 find_device_public_key(main.list_devices, i['id']))
        if find_mac_address(main.list_devices, i['id']) == i['mac'] and decrypted_message_verification:
            new_block.update({str(iterator): i})
            iterator += 1
            client.publish(helpers.utils.CORRECT_VALIDATION, i['id'])
        else:
            client.publish(helpers.utils.FALSE_VALIDATION, i['id'])
            print("fake block")
            return
    new_block.update({"time": str(datetime.datetime.utcnow())})
    client.publish(helpers.utils.NEW_BLOCK, BSON.encode(new_block))


def add_new_block(client, userdata, message):
    received_block = BSON.decode(message.payload)
    timestamp = received_block.pop("time")
    if main.block_chain.blocks.__len__() == 0:
        computed_block = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, timestamp, received_block)
        main.block_chain.blocks.append(computed_block)
    else:
        main.block_chain.add_block(timestamp, received_block)
        computed_block = main.block_chain.blocks[-1]
    print("New block mined!\n", computed_block)
    if main.is_miner is True:
        add_to_db(computed_block)
    del computed_block
    sleep(1)
    data_collector.prepare_device_block(client, userdata.get("priv_key"), userdata.get("id_device"), userdata.get("mac_address"))


def add_to_db(computed_block):
    db = dbconf.connect_to_db()
    copy_object = {
        'index': computed_block.index,
        'timestamp': computed_block.timestamp,
        'data': list(computed_block.data.values()),
        'previous hash': computed_block.previous_hash,
        'hash': computed_block.hash
    }
    db.insert_one(copy_object)


def add_trust_value(client, userdata, message):
    id_dev = str(message.payload, "UTF-8")
    try:
        trust_value = main.trusted_devices.get(id_dev) + 1
        main.trusted_devices.update({id_dev: trust_value})
    except TypeError:
        None


def decrement_trust_value(client, userdata, message):
    id_dev = str(message.payload, "UTF-8")
    try:
        trust_value = main.trusted_devices.get(id_dev) - 2
        main.trusted_devices.update({id_dev: trust_value})
    except TypeError:
        None


def choose_new_miner(client, userdata):
    #TODO check if not null!
    could_be_miner = dict(filter(lambda elem: int(elem[0]) > 10, main.trusted_devices.items()))
    print(could_be_miner)
    new_miner = random.choice(list(could_be_miner.keys()))
    client.publish(helpers.utils.CHOOSE_MINER, new_miner)


def new_miner(client, userdata, message):
    if str(message.payload, "UTF-8") == userdata.get("id_device"):
        main.is_miner = True
    else:
        main.is_miner = False


def resend_device_info(client, userdata, message):
    tmp_object = json.loads(message.payload)
    if list(filter(lambda x: x.id == tmp_object['id'], main.list_devices)).__len__() == 0:
        main.list_devices.append(
            initialization.DeviceInfo(tmp_object['id'], tmp_object['mac_address'], "client/" + str(tmp_object['id']),
                                      tmp_object['public_key_e'], tmp_object['public_key_n']))
    client.publish(helpers.utils.PUB_KEYS_TOPIC, json.dumps(main.list_devices[0].__dict__))


def resend_trust_rate(client, userdata, message):
    temp = json.loads(message.payload)
    main.trusted_devices.update(temp)
    client.publish(helpers.utils.TRUST_RATE,
                   json.dumps({userdata.get("id_device"): int(main.trusted_devices.get(userdata.get("id_device")))}))


def delete_device(client, userdata, message):
    inactive_device_id = str(message.payload, "UTF-8")
    try:
        delete_device_from_storages(inactive_device_id)
        main.trusted_devices.pop(inactive_device_id)
    except KeyError:
        pass
