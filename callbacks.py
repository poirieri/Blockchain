import json
import bson
from rsa import PublicKey
import MinimalBlock
import initialization
import main
import security
from helpers.common_topics import SEND_ENCRYPTED_MESSAGE


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
    kubus = bson.loads(message.payload)
    decrypted_message_verification = security.verify_message(kubus['transactions'].encode(), kubus['signature'],
                                                             find_device(main.list_devices, kubus['id']))

    if find_mac_address(main.list_devices, kubus['id']) == kubus['mac'] and decrypted_message_verification == 1:
        print("verified " + str(decrypted_message_verification))
        main.temporary_blocks.append(kubus)
        if main.temporary_blocks.__len__() == 5:
            print("5 transakcji gotowe")
            if main.block_chain.blocks.__len__() == 0:
                main.block_chain = MinimalBlock.MinimalChain.get_genesis_block(main.block_chain, main.temporary_blocks)
                main.block_chain.blocks = [MinimalBlock.MinimalChain.get_genesis_block(main.block_chain,
                                                                                  main.temporary_blocks)]
            else:
                MinimalBlock.MinimalChain.add_block(main.block_chain, main.temporary_blocks)
            main.temporary_blocks.clear()


