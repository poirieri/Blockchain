import sys
import uuid
from random import randint
import Block
import security as bs

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
# host = "localhost"
host = str(sys.argv[3])
# port = 1883
port = int(sys.argv[4])
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
minimum_nodes = 2
database = None
