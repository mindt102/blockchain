import threading
import time

import yaml

import utils
from api import api_thread
from blockchain import blockchain
from Miner import miner
from network import network
from Role import Role

if __name__ == '__main__':
    __logger = utils.get_logger(__name__)
    try:
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        run_event = threading.Event()
        run_event.set()

        blockchain.start()
        network.start()
        miner.start()
        api_thread.start()

        while True:
            # Keep the main thread alive to support keyboard interrupts
            time.sleep(.1)

    except KeyboardInterrupt:
        __logger.info("Keyboard interrupt. Stopping node")
        Role.deactivate()
        miner.join()
        __logger.info("Miner stopped")
        network.join()
        __logger.info("Network stopped")
        blockchain.join()
        __logger.info("Blockchain stopped")
        exit(0)
    except:
        __logger.exception("Could not start node. Please check config.yml")
        raise

# https://cs.berry.edu/~nhamid/p2p/index.html
