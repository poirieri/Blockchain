from Blockchain import initialization
import Blockchain.global_variables as gl
import logging
import sys
import Blockchain.dbconf as db


def main():
    if gl.is_debug == "DEBUG":
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("ID device: " + gl.id_device)
    client = initialization.connect_client(gl.id_device, gl.mac_address, gl.keys)
    gl.database = db.connect_to_db()
    initialization.send_device_info(client, gl.keys, gl.id_device, gl.mac_address, gl.trust_rate)
    client.loop_forever()


if __name__ == '__main__':
    main()


