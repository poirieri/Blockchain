import asyncio
import datetime
import time
from random import randint
from Blockchain import security
import Blockchain.global_variables as gl
import psutil
import json


async def transaction():
    """Append transactions list."""
    x = 5
    # gl.transactions.append("Data: str(datetime.datetime.now())[:19]" + "Temperatura: 24," + x + " °C")
    gl.transactions.append({"Name": "Stan baterii",
                           "Date": str(datetime.datetime.now())[:19],
                           "Value": str(psutil.sensors_battery().percent)})
    # gl.transactions.append("Data: str(datetime.datetime.now())[:19]" + "Ciśnienie: 1019 hPa")oki
    time.sleep(x)


async def gather_transactions(client):
    """Gather transactions in transaction list."""
    return await asyncio.gather(transaction())


def prepare_transactions_block(client, private_key, id_device, mac_address):
    """Prepare transaction block containing id, mac_address, signature and set of transactions.
    :param client:
    :param private_key:
    :param id_device:
    :param mac_address:
    """
    asyncio.run(gather_transactions(client))
    list_to_str = json.dumps(gl.transactions)
    signature = security.sign_message(list_to_str, private_key)
    data_set = {
        "id": id_device,
        "mac": mac_address,
        "signature": signature,
        "transactions": list_to_str
        }
    return data_set

