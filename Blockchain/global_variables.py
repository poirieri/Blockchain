import sys
import uuid
from random import randint
from Blockchain import Block
import Blockchain.security as bs

id_device = None
list_devices = []
transactions = {}
keys = None
temporary_blocks = []
block_chain = Block.Chain()
trusted_devices = {}
is_miner = bool(int(sys.argv[1]))
is_debug = "DEBUG"
sensor = int(sys.argv[2])
# host = "192.168.0.206"
host = "localhost"
port = 1883
mac_address = hex(uuid.getnode())
trust_rate = 10 if is_miner else 8
id_device = str(randint(0, 100000))
keys = bs.configure_keys()
is_mining = False
