import yaml

import utils
from blockchain import Blockchain
from database.dbTable import createDb
from Miner import Miner
from network import Network
from Wallet import Wallet

if __name__ == '__main__':

    logger = utils.get_logger(__name__)
    try:
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        # createDb(config['db']['name'], config['db']
        #          ['sample'], config['db']['debug'])

        network = Network(config=config["network"])
        network.start()

        blockchain = Blockchain(
            config=config["blockchain"], db_config=config["db"])

        wallet = Wallet()

        miner = Miner(config=config["miner"])

        blockchain.start()
        miner.start()

    except:
        logger.exception("Could not start node. Please check config.yml")
        raise

# https://cs.berry.edu/~nhamid/p2p/index.html
