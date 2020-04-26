import asyncio
import sys
import time
import uuid
from random import randint
import data_collector
import initialization
import MinimalBlock

list_devices = []
id_device = randint(0, 100000)
transactions = []
keys = None
temporary_blocks = []
block_chain = MinimalBlock.MinimalChain()
trusted_devices = {}
trust_rate = int(sys.argv[1])
isMiner = bool(sys.argv[2])
mac_address = hex(uuid.getnode())


def main():
    client = initialization.configure_client()
    keys = initialization.configure_keys()
    initialization.send_device_info(client, keys, id_device, mac_address, trust_rate)
    data_collector.prepare_device_block(client, keys[1], id_device, mac_address)
    client.loop_forever()

if __name__ == '__main__':
    main()
