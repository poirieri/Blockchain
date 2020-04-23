from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def connect_to_db():
    try:
        conn = MongoClient()
        print("Connected successfully!!!")
    except ConnectionFailure:
        print("Could not connect to MongoDB")

    db = conn.database   # database
    collection = db.blockchain    # Created or Switched to collection
    return collection
