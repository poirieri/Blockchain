import asyncio
from random import randint
from MinimalBlock import *
import gather_transactions
from initialization import *

list_devices = []
ID = randint(0, 100000)
transactions = []
keys = None
temporary_blocks = {}
if __name__ == '__main__':
    client = configure_client()
    keys = configure_keys(keys)
    device_info = prepare_device_info(keys)
    send_keys(client, device_info)
    asyncio.run(gather_transactions.gather_transactions(client))
    block = gather_transactions.prepare_device_block(keys[1], keys[0])
    send_block(client, block)
    client.loop_forever()
