import socket

import yaml
from database.dbTable import createDb

import utils
# from blockchain import Blockchain
from Miner import Miner
from network import Network
from Wallet import Wallet

from blockchain import Blockchain, BlockHeader

if __name__ == '__main__':

    logger = utils.get_logger(__name__)
    try:
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        createDb(config['db']['name'], config['db']
                 ['sample'], config['db']['debug'])

        # network = Network(config=config["network"])
        # network.start()

        blockchain = Blockchain(config=config["blockchain"])
        block = blockchain.get_genesis_block()
        block.insert()
        # print(.get_header().insert())
        # wallet = Wallet()

        # miner = Miner(config=config["miner"])

        # blockchain.start()
        # miner.start()

    except:
        logger.exception("Could not start node. Please check config.yml")
        raise

# https://cs.berry.edu/~nhamid/p2p/index.html
