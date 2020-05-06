import sys
import uuid
from Blockchain import MinimalBlock

id_device = None
list_devices = []
transactions = []
keys = None
temporary_blocks = []
block_chain = MinimalBlock.MinimalChain()
trusted_devices = {}
trust_rate = int(sys.argv[1])
is_miner = bool(int(sys.argv[2]))
mac_address = hex(uuid.getnode())
