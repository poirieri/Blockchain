import time
from random import randint
from Blockchain import initialization, data_collector
import Blockchain.global_variables as gl
import logging, sys


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    gl.id_device = str(randint(0, 100000))
    logging.debug("ID device: " + gl.id_device)
    gl.keys = initialization.configure_keys()
    client = initialization.configure_client(gl.id_device, gl.is_miner, gl.mac_address, gl.keys)
    initialization.send_device_info(client, gl.keys, gl.id_device, gl.mac_address, gl.trust_rate)
    client.loop_forever()

# TODO Check why no error but mining blocks stop


if __name__ == '__main__':
    main()


"""
TO DO
1. Fix too much sending dev info
2.what if another 2 devices have trust rate
2. Delete sending trust_rate -> merge!!
"""