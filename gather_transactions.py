import asyncio
import datetime
import uuid
import bson
import main
import security
from bson import BSON


async def transaction():
    main.transactions.append("transaction" + str(datetime.datetime.now()))
    await asyncio.sleep(2)


async def gather_transactions(client):
    await asyncio.gather(transaction(), transaction(), transaction())


def prepare_device_block(private_key):
    list_to_str = ';'.join(map(str, main.transactions))
    signature = security.sign_message(list_to_str, private_key)
    mac_address = hex(uuid.getnode())
    data_set = {
        "id": main.ID,
        "mac": mac_address,
        "signature": signature,
        "transactions": list_to_str
        }
    return BSON.encode(data_set)
