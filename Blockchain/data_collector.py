import asyncio
import datetime
from random import randint

from bson import BSON

from Blockchain import security
import Blockchain.global_variables as gl
import psutil
import json


async def transaction():
    """Append transactions list."""
    if gl.sensor == 1:
        gl.transactions = {"Name": "Stan baterii",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(psutil.sensors_battery().percent)}
    elif gl.sensor == 2:
        y = str(randint(4, 5))
        x = "24," + y
        gl.transactions = {"Name": "Temperatura",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 3:
        gl.transactions = {"Name": "Stan baterii",
                            "Date": str(datetime.datetime.now())[:19],
                            "Value": str(psutil.sensors_battery().percent)}
    elif gl.sensor == 4:
        x = 1023
        gl.transactions = {"Name": "Ciśnienie",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 5:
        x = 11
        gl.transactions = {"Name": "Wiatr",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 6:
        x = 0
        gl.transactions = {"Name": "Śnieg",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 7:
        x = 0
        gl.transactions = {"Name": "Deszcz",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 8:
        x = 8
        gl.transactions = {"Name": "PM 2.5",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 9:
        x = 6
        gl.transactions = {"Name": "PM 10",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}

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
    gl.transactions.clear()
    asyncio.run(gather_transactions(client))
    transaction = json.dumps(gl.transactions)
    signature = security.sign_message(transaction, private_key)
    data_set = {
        "id": id_device,
        "mac": mac_address,
        "signature": signature.decode(encoding='latin1'),
        "transactions": json.dumps(transaction)
        }
    return data_set

# b = signature.decode(encoding='latin1')
# c = b.encode(encoding='latin1')
