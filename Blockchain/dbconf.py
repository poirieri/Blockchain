import json
import logging
import Blockchain.global_variables as gl
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def connect_to_db():
    """ Connect to created database
    :return: created collection
    """
    try:
        conn = MongoClient()
        # conn = MongoClient("192.168.0.206", 27017)
        logging.debug("DB: Connected successfully!!!")
    except ConnectionFailure:
        logging.debug("Could not connect to MongoDB")

    db = conn.database   # database
    collection = db.blockchain    # Created or Switched to collection
    return collection


def add_to_db(mined_block):
    """ Add newly mined block to chain of blocks
    :param mined_block: set of validated blocks from different devices with hash values
    :return:
    """
    db = connect_to_db()
    # for i in mined_block.data:
    #     mined_block.data[i]['transactions'] = json.loads(mined_block.data[i]['transactions'])
    copy_object = {
        'index': mined_block.index,
        'timestamp': mined_block.timestamp,
        'data': list(mined_block.data.values()),
        'previous hash': mined_block.previous_hash,
        'hash': mined_block.hash,
        'miner': gl.id_device
    }
    db.insert_one(copy_object)
    print("inserted")
