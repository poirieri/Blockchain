import asyncio
import datetime
import time
from random import randint

from bson import BSON

from Blockchain import security
import Blockchain.global_variables as gl
import psutil
import json


async def transaction():
    """Append transactions list."""
    if gl.sensor == 1:
        time.sleep(randint(30, 60))
        gl.transactions = {"Name": "Stan baterii",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(99)}
    elif gl.sensor == 2:
        time.sleep(randint(5, 15))
        y = str(randint(4, 5))
        x = "24." + y
        gl.transactions = {"Name": "Temperatura 1",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 3:
        time.sleep(randint(50, 60))
        y = str(randint(8, 9))
        x = "18." + y
        gl.transactions = {"Name": "Temperatura 2",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 4:
        time.sleep(randint(20, 30))
        x = 1023
        gl.transactions = {"Name": "Ciśnienie",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 5:
        time.sleep(randint(50, 60))
        x = 11
        gl.transactions = {"Name": "Wiatr",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 6:
        time.sleep(randint(60, 120))
        x = 0
        gl.transactions = {"Name": "Śnieg",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 7:
        time.sleep(randint(60, 120))
        x = 0
        gl.transactions = {"Name": "Deszcz",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 8:
        time.sleep(randint(100, 120))
        x = 8
        gl.transactions = {"Name": "PM 2.5",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    elif gl.sensor == 9:
        time.sleep(randint(100, 120))
        x = 6
        gl.transactions = {"Name": "PM 10",
                                "Date": str(datetime.datetime.now())[:19],
                                "Value": str(x)}
    else:
        x = 6
        time.sleep(randint(100, 120))
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
        "transactions": transaction
        }
    return data_set

