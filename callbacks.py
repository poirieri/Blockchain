import json
import bson
from rsa import PublicKey

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


def send_encrypted(data, dev):
    device = find_device(main.list_devices, dev.id)
    message = security.encrypt(data, PublicKey(device.public_key_n, device.public_key_e))
    initialization.client.publish(SEND_ENCRYPTED_MESSAGE + str(dev.id), message)
    print(device.public_key_n, device.public_key_e)
    print("wysylam wiadomosc do urzadzenia " + str(dev.id))


def decrypt_callback(client, userdata, message):
    main.temporary_blocks.update({"1": message.payload})
    kubus = bson.loads(message.payload)
    decrypted_message = security.verify_message(kubus['transactions'].encode(), kubus['signature'],
                                                find_device(main.list_devices, kubus['id']))
    print(decrypted_message)
