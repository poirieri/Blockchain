import copy
import datetime
import hashlib
import json
import time
from random import randint

from rsa import PublicKey

import security
import paho.mqtt.client as mqtt
from Blockchain.helpers.common_topics import *
from json import JSONEncoder


# ID = randint(0, 100000)
#
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))
#
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("test")
#     client.subscribe(TEST)
#     client.subscribe(PUB_KEYS_TOPIC)
#     client.subscribe(SEND_ENCRYPTED_MESSAGE + str(ID))
#
#
# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))
# ## Simple blockchain implementation
from Blockchain.initialization import configure_client, configureKeys, configure_keys


class Buffer:
    def __init__(self):
        self.index = 0
        self.timestamp = 0
        self.data = 0
    def encrypt_data(self, timestamp, data):

        self.index = self.index + 1

class MinimalBlock:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hashing()

    def hashing(self):
        key = hashlib.sha256()
        key.update(str(self.index).encode('utf-8'))
        key.update(str(self.timestamp).encode('utf-8'))
        key.update(str(self.data).encode('utf-8'))
        key.update(str(self.previous_hash).encode('utf-8'))
        return key.hexdigest()



class MinimalChain:
    def __init__(self): #initialize when creating a chain
        self.blocks = [self.get_genesis_block()]

    def get_genesis_block(self):
        return MinimalBlock(0,
                            str(datetime.datetime.utcnow()),
                            "DATA",
                            'arbitrary')

    def add_block(self, data):
        self.blocks.append(MinimalBlock(len(self.blocks),
                                        datetime.datetime.utcnow(),
                                        data,
                                        self.blocks[len(self.blocks)-1].hash))

    def get_chain_size(self):  # excl;ude genesis block
        return len(self.blocks)-1

    def verify(self, verbose=True):
        flag = True
        for i in range(1,len(self.blocks)):
            if self.blocks[i - 1].hash != self.blocks[i].previous_hash:
                flag = False
                if verbose:
                    print(f'Wrong previous hash at block {i}.')
            if self.blocks[i].hash != self.blocks[i].hashing():
                flag = False
                if verbose:
                    print(f'Wrong hash at block {i}.')
            if self.blocks[i - 1].timestamp >= self.blocks[i].timestamp:
                flag = False
                if verbose:
                    print(f'Backdating at block {i}.')
            return flag

            def fork(self, head='latest'):
                if head in ['latest', 'whole', 'all']:
                    return copy.deepcopy(self)  # deepcopy since they are mutable
                else:
                    c = copy.deepcopy(self)
                    c.blocks = c.blocks[0:head + 1]
                    return c

            def get_root(self, chain_2):
                min_chain_size = min(self.get_chain_size(), chain_2.get_chain_size())
                for i in range(1, min_chain_size + 1):
                    if self.blocks[i] != chain_2.blocks[i]:
                        return self.fork(i - 1)
                return self.fork(min_chain_size)


# def configure_client():
#     client = mqtt.Client()
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect("localhost", 1883, 60)
#     return client


def add_key_to_keystore(client, userdata, message):
    message.payload


# def json_create_obj(data):
#     for key in data.keys():
#         print(data[key])

def prepare_json_to_send(data):
    data_set = {
        "id" : ID,
        "data" : {
           "e" : data[0].e,
            "n" : data[0].n
        }
    }
    return json.dumps(data_set)


class DeviceInfo:

    def __init__(self, id, mac_address, topic, public_key_e, public_key_n):
        self.id = id
        self.mac_address = mac_address
        self.topic = topic
        self.public_key_e = public_key_e
        self.public_key_n = public_key_n

def pump_callback(client, userdata, message):
    tmp_obiect = json.loads(message.payload)
    list_devices.append(DeviceInfo(tmp_obiect['id'], "client/" + str(tmp_obiect['id']), tmp_obiect['data']['e'], tmp_obiect['data']['n']))

    # print(message.payload)
    print(list_devices)
    find_device(list_devices, tmp_obiect['id'])
    send_encrypted("data", list_devices[len(list_devices)-1])

def find_device(list_devices, id):
    filter_obj = list(filter(lambda x: x.id == id, list_devices))
    return filter_obj[0]

def send_encrypted(data, dev):
    device = find_device(list_devices, dev.id)
    message = security.encrypt(data, PublicKey(device.public_key_n, device.public_key_e))
    client.publish(SEND_ENCRYPTED_MESSAGE + str(dev.id), message)
    print(device.public_key_n, device.public_key_e)
    print("wysylam wiadomosc do urzadzenia " + str(dev.id))

def decrypt_callback(client, userdata, message):
    decrypted_message = security.decrypt(message.payload, keys[1])
    print(decrypted_message)
    return decrypted_message

class aBlockEncoder(JSONEncoder):

    def default(self, object):

        if isinstance(object, MinimalBlock):

            return object.__dict__

        else:

            return json.JSONEncoder.default(self, object)


if __name__ == '__main__':
    ID = randint(0, 100000)
    list_devices = []
    keys = None

    client = configure_client()
    keys = configure_keys()


    client.message_callback_add(PUB_KEYS_TOPIC, pump_callback)
    client.message_callback_add(SEND_ENCRYPTED_MESSAGE + str(ID), decrypt_callback)

    testowy_block = MinimalChain
    a = testowy_block.get_genesis_block(testowy_block)

    json_string = aBlockEncoder().encode(a)

    client.publish(TEST,  payload=json_string)

    client.loop_forever()
