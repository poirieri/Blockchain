from random import randint
from Blockchain import initialization, data_collector
import Blockchain.global_variables as gl


def main():
    gl.id_device = str(randint(0, 100000))
    gl.keys = initialization.configure_keys()
    client = initialization.configure_client(gl.id_device, gl.is_miner, gl.mac_address, gl.keys)
    initialization.send_device_info(client, gl.keys, gl.id_device, gl.mac_address, gl.trust_rate)
    data_collector.prepare_transactions_block(client, gl.keys[1], gl.id_device, gl.mac_address)
    client.loop_forever()


if __name__ == '__main__':
    main()