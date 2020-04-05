import asyncio
import datetime
import json

import helpers.common_topics
import main

async def transaction():
    main.transactions.append("transaction" + str(datetime.datetime.now()))
    await asyncio.sleep(2)


async def gather_transactions():
    await asyncio.gather(transaction(), transaction(), transaction())
    main.client.publish(helpers.common_topics.SEND_ENCRYPTED_MESSAGE, json.dumps(main.transactions))

