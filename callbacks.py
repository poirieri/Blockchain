import json
import bson
from rsa import PublicKey
import MinimalBlock
import dbconf
import initialization
import main
import security
from helpers.common_topics import SEND_ENCRYPTED_MESSAGE, MAXIMUM_BLOCK_SIZE
from bson import BSON
import helpers.utils

def add_key_to_keystore(client, userdata, message):
    message.payload


def public_keys_callback(client, userdata, message):
    tmp_object = json.loads(message.payload)
    main.list_devices.append(
        initialization.DeviceInfo(tmp_object['id'], tmp_object['mac_address'], "client/" + str(tmp_object['id']),
                                  tmp_object['public_key_e'], tmp_object['public_key_n']))


def find_device(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, list_devices))
    return PublicKey(filter_obj[0].public_key_n, filter_obj[0].public_key_e)

def find_mac_address(list_devices, id_device):
    filter_obj = list(filter(lambda x: x.id == id_device, list_devices))
    return filter_obj[0].mac_address

def send_encrypted(data, dev):
    device = find_device(main.list_devices, dev.id)
    message = security.encrypt(data, PublicKey(device.public_key_n, device.public_key_e))
    initialization.client.publish(SEND_ENCRYPTED_MESSAGE + str(dev.id), message)
    print(device.public_key_n, device.public_key_e)
    print("wysylam wiadomosc do urzadzenia " + str(dev.id))


def decrypt_callback(client, userdata, message):
    kubus = BSON.decode(message.payload)
    main.temporary_blocks.append(kubus)
    if main.temporary_blocks.__len__() == 2:
        if main.isMiner:
            iterator = 0
            for i in main.temporary_blocks:
                try:
                    decrypted_message_verification = security.verify_message(i['transactions'].encode(),
                                                                             i['signature'],
                                                                             find_device(main.list_devices, i['id']))
                    if find_mac_address(main.list_devices, i['id']) == i['mac'] and decrypted_message_verification == 1:
                        main.newblock.update({str(iterator) : i})
                        iterator = iterator + 1
                except ValueError:
                    print("Some error")
            # main.block_chain.blocks = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, main.newblock)
            # client.publish(helpers.utils.NEW_BLOCK, BSON.encode(main.block_chain.blocks.__dict__))
#TODO send object list and receive it
            client.publish(helpers.utils.NEW_BLOCK, BSON.encode(main.newblock))
            main.temporary_blocks.clear()

    # decrypted_message_verification = security.verify_message(kubus['transactions'].encode(), kubus['signature'],
    #                                                          find_device(main.list_devices, kubus['id']))
    #
    # if find_mac_address(main.list_devices, kubus['id']) == kubus['mac'] and decrypted_message_verification == 1:
    #     print("verified " + str(decrypted_message_verification))
    #     client.publish()
    #     main.temporary_blocks.append(kubus)
    #     if main.temporary_blocks.__len__() == 5:
    #         print("5 transakcji gotowe")
    #         if main.block_chain.blocks.__len__() == 0:
    #             main.block_chain = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, main.temporary_blocks)
    #             main.block_chain.blocks = [MinimalBlock.MinimalChain.get_genesis_block(main.block_chain,
    #                                                                               main.temporary_blocks)]
    #         else:
    #             MinimalBlock.MinimalChain.add_block(main.block_chain, main.temporary_blocks)
    #         main.temporary_blocks.clear()


def choose_trusted_device(client, userdata, message):
    main.trusted_devices
    client.publish(helpers.utils.CHECK_BLOCK)


def add_trust_rate(client, userdata, message):
    temp = json.loads(message.payload)
    main.trusted_devices.update(temp)

def add_new_block(client, userdata, message):
    received_block = BSON.decode(message.payload)
    if main.block_chain.blocks.__len__() == 0:
        main.block_chain = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, received_block)
        computed_block = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain,
                                                                          received_block)
    else:
        computed_block = MinimalBlock.MinimalChain.add_block(main.block_chain, received_block)


    db = dbconf.dbconnect(main.ID)
    copy_object = {
        'index': computed_block.index,
        'timestamp': computed_block.timestamp,
         'data': list(computed_block.data.values()),
         'previous hash': computed_block.previous_hash,
         'hash': computed_block.hash
         }

    rec_id1 = db.insert_one(copy_object)
    computed_block.clear()

