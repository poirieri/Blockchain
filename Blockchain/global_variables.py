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
is_miner = int(sys.argv[1])
is_debug = "DEBUG"
sensor = int(sys.argv[2])
# host = "192.168.0.206"
host = "localhost"
port = 1883
mac_address = hex(uuid.getnode())
if is_miner == 1:
    trust_rate = 10
elif is_miner == 0:
    trust_rate = 0
elif is_miner == 2:
    trust_rate = 10
    is_miner = 0
id_device = str(randint(0, 100000))
keys = bs.configure_keys()
is_mining = False
database = None
