import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def connect_to_db():
    """ Connect to created database
    :return: created collection
    """
    try:
        conn = MongoClient()
        logging.debug("Connected successfully!!!")
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
    copy_object = {
        'index': mined_block.index,
        'timestamp': mined_block.timestamp,
        'data': list(mined_block.data.values()),
        'previous hash': mined_block.previous_hash,
        'hash': mined_block.hash
    }
    db.insert_one(copy_object)
