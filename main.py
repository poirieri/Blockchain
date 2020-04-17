import asyncio
import sys
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
newblock = []


def main():
    client = initialization.configure_client()
    keys = initialization.configure_keys()
    device_info = initialization.prepare_device_info(keys)
    initialization.send_keys(client, device_info)
    initialization.send_trust_rate(client, trust_rate)
    asyncio.run(gather_transactions.gather_transactions(client))
    block = gather_transactions.prepare_device_block(keys[1])
    initialization.send_block(client, block)
    client.loop_forever()

if __name__ == '__main__':
    main()
