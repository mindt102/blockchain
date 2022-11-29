
import socket

import yaml

import utils
from blockchain import Blockchain
from Miner import Miner
from network import Network
from Wallet import Wallet

if __name__ == '__main__':
    logger = utils.get_logger(__name__)
    try:
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

        host = socket.gethostbyname(
            config["host"] if "host" in config else socket.gethostname())
        port = config["port"] if "port" in config else 8333
        maxpeers = config["maxpeers"] if "maxpeers" in config else 8

        known_nodes = config["known_nodes"]
        if len(known_nodes) == 0:
            raise RuntimeError(
                f"Must provide at least one known node. Current known_nodes: {known_nodes}")

        network = Network(host, port, maxpeers=maxpeers)
        network.start()
        network.discover_peers(known_nodes)

        blockchain = Blockchain(config=config["blockchain"])
        wallet = Wallet()
        miner = Miner(config=config["miner"])
        blockchain.start()
        miner.start()

    except:
        logger.exception("Could not start node. Please check config.yml")
        raise

# https://cs.berry.edu/~nhamid/p2p/index.html
