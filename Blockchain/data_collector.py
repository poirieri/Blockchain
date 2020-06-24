import asyncio
import datetime
import time
from random import randint
from Blockchain import security
import Blockchain.global_variables as gl


async def transaction():
    """Append transactions list."""
    gl.transactions.append("Temperatura: 24,5 °C")
    time.sleep(randint(0, 10))


async def gather_transactions(client):
    """Gather transactions in transaction list."""
    return await asyncio.gather(transaction(), transaction(), transaction())


def prepare_transactions_block(client, private_key, id_device, mac_address):
    """Prepare transaction block containing id, mac_address, signature and set of transactions.
    :param client:
    :param private_key:
    :param id_device:
    :param mac_address:
    """
    asyncio.run(gather_transactions(client))
    list_to_str = ';'.join(map(str, gl.transactions))
    signature = security.sign_message(list_to_str, private_key)
    data_set = {
        "id": id_device,
        "mac": mac_address,
        "signature": signature,
        "transactions": list_to_str
        }
    return data_set

