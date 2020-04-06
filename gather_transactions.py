import asyncio
import datetime
import json

import helpers.common_topics
import main
import security

async def transaction():
    main.transactions.append("transaction" + str(datetime.datetime.now()))
    await asyncio.sleep(2)


async def gather_transactions(client):
    await asyncio.gather(transaction(), transaction(), transaction())
    # client.publish(helpers.common_topics.SEND_ENCRYPTED_MESSAGE, json.dumps(main.transactions))

def prepare_device_block(priv_key):
    listToStr = ';'.join(map(str, main.transactions))
    signature = security.signMessage(listToStr, priv_key)
    data_set = {
        "id": main.ID,
        "signature": str(signature),
        "transactions": listToStr
        }
    return json.dumps(data_set)
