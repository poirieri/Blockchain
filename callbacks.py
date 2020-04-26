import json
import random

from rsa import PublicKey
import MinimalBlock
import dbconf
import initialization
import main
import security
from bson import BSON
import helpers.utils


def add_device_info_to_store(client, userdata, message):
    tmp_object = json.loads(message.payload)
    main.list_devices.append(
        initialization.DeviceInfo(tmp_object['id'], tmp_object['mac_address'], "client/" + str(tmp_object['id']),
                                  tmp_object['public_key_e'], tmp_object['public_key_n']))


def add_trust_rate_to_store(client, userdata, message):
    temp = json.loads(message.payload)
    main.trusted_devices.update(temp)


def find_device(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, list_devices))
    return PublicKey(filter_obj[0].public_key_n, filter_obj[0].public_key_e)


def find_mac_address(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, list_devices))
    return filter_obj[0].mac_address


def receive_encrypted_block(client, userdata, message):
    kubus = BSON.decode(message.payload)
    main.temporary_blocks.append(kubus)
    if main.temporary_blocks.__len__() == 2 and main.isMiner:
        validate_blocks(client, main.temporary_blocks)
        main.temporary_blocks.clear()
        choose_new_miner(client)


def validate_blocks(client, validated_blocks):
    iterator = 0
    new_block = dict()
    for i in validated_blocks:
        decrypted_message_verification = security.verify_message(i['transactions'].encode(),
                                                                 i['signature'],
                                                                 find_device(main.list_devices, i['id']))
        if find_mac_address(main.list_devices, i['id']) == i['mac'] and decrypted_message_verification:
            new_block.update({str(iterator): i})
            iterator += 1
            client.publish(helpers.utils.CORRECT_VALIDATION, i['id'])
        else:
            client.publish(helpers.utils.FALSE_VALIDATION, i['id'])
            print("fake block")
            return
    client.publish(helpers.utils.NEW_BLOCK, BSON.encode(new_block))

# def choose_trusted_device(client, userdata, message):
#     filter(main.trusted_devices)
#     client.publish(helpers.utils.CHECK_BLOCK, )


def add_new_block(client, userdata, message):
    received_block = BSON.decode(message.payload)
    if main.block_chain.blocks.__len__() == 0:
        main.block_chain = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, received_block)
        computed_block = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain,
                                                                          received_block)
    else:
        computed_block = MinimalBlock.MinimalChain.add_block(main.block_chain, received_block)
    add_to_db(computed_block)
    del computed_block


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
    trust_value = main.trusted_devices.get(id_dev)
    main.trusted_devices.update({str(id_dev): str(trust_value + 1)})


def decrement_trust_value(client, userdata, message):
    id_dev = str(message.payload, "UTF-8")
    trust_value = main.trusted_devices.get(id_dev)
    main.trusted_devices.update({str(id_dev): str(trust_value - 2)})


def choose_new_miner(client):
    could_be_miner = dict(filter(lambda elem: (elem[1]) > 4, main.trusted_devices.items()))
    print(could_be_miner)
    new_miner = random.choice(list(could_be_miner.keys()))
    client.publish(helpers.utils.CHOOSE_MINER, new_miner)


def new_miner(client, userdata, message):
    if str(message.payload, "UTF-8") == main.id_device:
        main.isMiner = True
    else:
        main.isMiner = False
#TODO reassure that everyone has the same device list and trustrate list