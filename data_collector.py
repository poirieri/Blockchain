import asyncio
import datetime
import initialization
import main
import security
from bson import BSON


async def transaction():
    main.transactions.append("data collection" + str(datetime.datetime.now()))
    await asyncio.sleep(2)


async def gather_transactions(client):
    await asyncio.gather(transaction(), transaction(), transaction())


def prepare_device_block(client, private_key, id, mac_address):
    asyncio.run(gather_transactions(client))
    list_to_str = ';'.join(map(str, main.transactions))
    signature = security.sign_message(list_to_str, private_key)
    data_set = {
        "id": id,
        "mac": mac_address,
        "signature": signature,
        "transactions": list_to_str
        }
    initialization.send_block(client, BSON.encode(data_set))

