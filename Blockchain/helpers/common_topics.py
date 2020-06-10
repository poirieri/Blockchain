SYS_BROKER_CLIENTS_CONNECTED = "$SYS/broker/clients/connected"
SYS_BROKER_BYTES_RECEIVED = "$SYS/broker/load/bytes/received"
SYS_BROKER_BYTES_SEND = "$SYS/broker/load/bytes/sent"
SYS_BROKER_NUMBER_CLIENTS_CONNECTED = "$SYS/broker/clients/total"

""" TOPICS ABBREVIATIONS
tv - trust value topics
dev_info - device info topics
sb - single block
"""

NEW_DEVICE_INFO = "dev_info/send"
NEW_DEVICE_INFO_RESPOND = "dev_info/respond"
SEND_ENCRYPTED_MESSAGE = "sb/encrypted"
NEW_BLOCK = "block/new"
DEVICE_OFFLINE = "offline"
NEW_DEVICE_TRUST_RATE = "tv/new"
CHOOSE_MINER = "tv/choose"
RESPOND_WITH_OWN_TRUST_RATE = "tv/respond"
FALSE_VALIDATION = "tv/decrement"
CORRECT_VALIDATION = "tv/add"
CLIENT = "client/"
