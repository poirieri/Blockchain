import asyncio
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

if __name__ == '__main__':
    client = initialization.configure_client()
    keys = initialization.configure_keys(keys)
    device_info = initialization.prepare_device_info(keys)
    initialization.send_keys(client, device_info)
    asyncio.run(gather_transactions.gather_transactions(client))
    block = gather_transactions.prepare_device_block(keys[1])
    initialization.send_block(client, block)
    client.loop_forever()
