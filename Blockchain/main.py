from Blockchain import initialization
import Blockchain.global_variables as gl
import logging
import sys

"""
TO DO
1. Fix too much sending dev info -> Delete sending trust_rate -> merge!!
2. What if another 2 devices have trust rate 1stone is miner -> send appropriate message or get info from broker
3. Perform a healthcheck every x minutes
4. Give trust point for good validation and take away when wrong validation ->each own 
"""


def main():
    if gl.is_debug == "DEBUG":
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug("ID device: " + gl.id_device)
    client = initialization.configure_client(gl.id_device, gl.is_miner, gl.mac_address, gl.keys)
    initialization.send_device_info(gl.keys, gl.id_device, gl.mac_address, gl.trust_rate)
    client.loop_forever()


if __name__ == '__main__':
    main()


