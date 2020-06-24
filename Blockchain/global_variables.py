import sys
import uuid
from random import randint
from Blockchain import Block
import Blockchain.security as bs

id_device = None
list_devices = []
transactions = []
keys = None
temporary_blocks = []
block_chain = Block.Chain()
trusted_devices = {}
is_miner = bool(int(sys.argv[1]))
is_debug = str(sys.argv[2])
host = "192.168.0.206" #str(sys.argv[3])
port = 1883 #int(sys.argv[4])
mac_address = hex(uuid.getnode())
trust_rate = 10 if is_miner else 0
id_device = str(randint(0, 100000))
keys = bs.configure_keys()
