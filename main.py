import threading
import time
import yaml
from Role import Role

import utils
from blockchain import Blockchain
from Miner import Miner
from network import Network
from Wallet import Wallet

if __name__ == '__main__':

    logger = utils.get_logger(__name__)
    try:
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        run_event = threading.Event()
        run_event.set()

        blockchain = Blockchain(
            config=config["blockchain"],
            db_config=config["db"]
        )

        network = Network(config=config["network"])

        wallet = Wallet()

        miner = Miner(config=config["miner"])

        # blockchain.start()
        # network.start()
        # miner.start()
        # wallet.start()

        # while True:
        #     time.sleep(0.1)

        import database
        print(len(database.get_utxo('test')))
        print(Wallet.get_addr())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt. Stopping node")
        Role.deactivate()
        # miner.join()
        logger.info("Miner stopped")
        # network.join()
        logger.info("Network stopped")
        # blockchain.join()
        logger.info("Blockchain stopped")
        wallet.join()
        logger.info("Wallet stopped")
    except:
        logger.exception("Could not start node. Please check config.yml")
        raise

# https://cs.berry.edu/~nhamid/p2p/index.html
