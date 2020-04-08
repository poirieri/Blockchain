import asyncio
import datetime
import json
import bson
import helpers.common_topics
import main
import security
import initialization
import helpers.utils

async def transaction():
    main.transactions.append("transaction" + str(datetime.datetime.now()))
    await asyncio.sleep(2)


async def gather_transactions(client):
    await asyncio.gather(transaction(), transaction(), transaction())
    # client.publish(helpers.common_topics.SEND_ENCRYPTED_MESSAGE, json.dumps(main.transactions))

def prepare_device_block(priv_key, pub):
    listToStr = ';'.join(map(str, main.transactions))
    signature = security.signMessage(listToStr, priv_key)
    # data_set = initialization.Block(main.ID, signature, listToStr)
    data_set = {
        "id": main.ID,
        "signature": signature,
        "transactions": listToStr
        }
    return bson.dumps(data_set)
    # return json.dumps(data_set)
    # return helpers.utils.bBlockEncoder().encode(data_set)
