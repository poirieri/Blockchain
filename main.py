import asyncio
from random import randint
from MinimalBlock import *
from gather_transactions import gather_transactions
from initialization import *

list_devices = []
ID = randint(0, 100000)
keys = None
transactions = []

if __name__ == '__main__':
    client = configure_client()
    keys = configure_keys(keys)
    device_info = prepare_device_info(keys)
    send_keys(client, device_info)
    asyncio.run(gather_transactions())

    client.loop_forever()
