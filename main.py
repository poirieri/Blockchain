import asyncio
import sys
import uuid
from random import randint
import gather_transactions
import initialization
import MinimalBlock

list_devices = []
ID = randint(0, 100000)
transactions = []
keys = None
temporary_blocks = []
block_chain = MinimalBlock.MinimalChain()
trusted_devices = {}
trust_rate = int(sys.argv[1])
isMiner = bool(sys.argv[2])
newblock = dict()
mac_address = hex(uuid.getnode())


def main():
    client = initialization.configure_client()
    keys = initialization.configure_keys()
    initialization.send_device_info(client, keys, ID, mac_address)

    asyncio.run(gather_transactions.gather_transactions(client))
    block = gather_transactions.prepare_device_block(keys[1])
    initialization.send_block(client, block)
    client.loop_forever()

if __name__ == '__main__':
    main()
