import datetime
import json
import random
from rsa import PublicKey
import MinimalBlock
import dbconf
import initialization
import security
from bson import BSON
import helpers.utils
from main import list_devices, trusted_devices, temporary_blocks
import main
import data_collector
MAX_BLOCKS = 1


def add_device_info_to_store(client, userdata, message):
    tmp_object = json.loads(message.payload)
    list_devices.append(
        initialization.DeviceInfo(tmp_object['id'], tmp_object['mac_address'], "client/" + str(tmp_object['id']),
                                  tmp_object['public_key_e'], tmp_object['public_key_n']))


def add_trust_rate_to_store(client, userdata, message):
    temp = json.loads(message.payload)
    trusted_devices.update(temp)


def find_device(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, list_devices))
    return PublicKey(filter_obj[0].public_key_n, filter_obj[0].public_key_e)


def find_mac_address(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, list_devices))
    return filter_obj[0].mac_address


def receive_encrypted_block(client, userdata, message):
    kubus = BSON.decode(message.payload)
    temporary_blocks.append(kubus)
    if temporary_blocks.__len__() == MAX_BLOCKS and userdata.get("isMiner") is True:
        validate_blocks(client, temporary_blocks)
        temporary_blocks.clear()
        choose_new_miner(client, userdata)


def validate_blocks(client, validated_blocks):
    iterator = 0
    new_block = dict()
    for i in validated_blocks:
        decrypted_message_verification = security.verify_message(i['transactions'].encode(),
                                                                 i['signature'],
                                                                 find_device(list_devices, i['id']))
        if find_mac_address(list_devices, i['id']) == i['mac'] and decrypted_message_verification:
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
    add_to_db(computed_block)
    del computed_block
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
    trust_value = trusted_devices.get(id_dev) + 1
    trusted_devices.update({id_dev: trust_value})


def decrement_trust_value(client, userdata, message):
    id_dev = str(message.payload, "UTF-8")
    trust_value = trusted_devices.get(id_dev) - 2
    trusted_devices.update({id_dev: trust_value})


def choose_new_miner(client, userdata):
    #TODO check if not null!
    could_be_miner = dict(filter(lambda elem: int(elem[0]) > 10, trusted_devices.items()))
    print(could_be_miner)
    new_miner = random.choice(list(could_be_miner.keys()))
    client.publish(helpers.utils.CHOOSE_MINER, new_miner)
    # data_collector.prepare_device_block(client, userdata.get("priv_key"), userdata.get("id_device"), userdata.get("mac_address"))


def new_miner(client, userdata, message):
    if str(message.payload, "UTF-8") == userdata.get("id_device"):
        client.user_data_set({"isMiner": True})
    else:
        client.user_data_set({"isMiner": False})


def resend_device_info(client, userdata, message):
    tmp_object = json.loads(message.payload)
    list_devices.append(
        initialization.DeviceInfo(tmp_object['id'], tmp_object['mac_address'], "client/" + str(tmp_object['id']),
                                  tmp_object['public_key_e'], tmp_object['public_key_n']))
    client.publish(helpers.utils.PUB_KEYS_TOPIC, json.dumps(list_devices[0].__dict__))


def resend_trust_rate(client, userdata, message):
    temp = json.loads(message.payload)
    trusted_devices.update(temp)
    client.publish(helpers.utils.TRUST_RATE,
                   json.dumps({userdata.get("id_device"): int(trusted_devices.get(userdata.get("id_device")))}))
