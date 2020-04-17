import json
import bson
from rsa import PublicKey
import MinimalBlock
import dbconf
import initialization
import main
import security
from helpers.common_topics import SEND_ENCRYPTED_MESSAGE, MAXIMUM_BLOCK_SIZE
import helpers.size_counter
from bson import BSON

def add_key_to_keystore(client, userdata, message):
    message.payload


def prepare_json_to_send(data):
    data_set = {
        "id": initialization.ID,
        "data": {
            "e": data[0].e,
            "n": data[0].n
        }
    }
    return json.dumps(data_set)


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
            for i in main.temporary_blocks:
                try:
                    decrypted_message_verification = security.verify_message(i['transactions'].encode(),
                                                                             i['signature'],
                                                                             find_device(main.list_devices, i['id']))
                    if find_mac_address(main.list_devices, i['id']) == i['mac'] and decrypted_message_verification == 1:
                        main.newblock.append(i)
                except ValueError:
                    print("Some error")
            main.block_chain.blocks = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, main.newblock)

            client.publish(helpers.utils.NEW_BLOCK, BSON.encode(main.block_chain.blocks.__dict__))
            main.temporary_blocks.clear()


        # choose_trusted_device(client)

    # decrypted_message_verification = security.verify_message(kubus['transactions'].encode(), kubus['signature'],
    #                                                          find_device(main.list_devices, kubus['id']))
    #
    # if find_mac_address(main.list_devices, kubus['id']) == kubus['mac'] and decrypted_message_verification == 1:
    #     print("verified " + str(decrypted_message_verification))
    #     client.publish()
    #     main.temporary_blocks.append(kubus)
    #     print(helpers.size_counter.total_size(main.block_chain.blocks, verbose=True))
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
    temp = BSON.decode(message.payload)
    main.trusted_devices.update(temp)

def add_new_block(client, userdata, message):
    print(BSON.decode(message.payload))
    db = dbconf.dbconnect()
    rec_id1 = db.insert_one(BSON.decode(message.payload))