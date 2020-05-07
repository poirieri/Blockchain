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
is_miner = bool(int(sys.argv[1]))
mac_address = hex(uuid.getnode())
trust_rate = 10 if is_miner is True else 0
