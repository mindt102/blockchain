from os import system
import threading
import time

import yaml

import utils
from api import app
from blockchain import Blockchain, blockchain
from Miner import Miner, miner
from network import Network, network
from Role import Role
from Wallet import Wallet

if __name__ == '__main__':
    __logger = utils.get_logger(__name__)
    try:
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        run_event = threading.Event()
        run_event.set()

        # blockchain = Blockchain(
        #     config=config["blockchain"],
        #     db_config=config["db"]
        # )

        # network = Network(config=config["network"])

        # wallet = Wallet()

        # miner = Miner(config=config["miner"])

        blockchain.start()
        network.start()
        miner.start()
        # wallet.start()

        # app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

        api_thread = threading.Thread(target=lambda: app.run(
            host="0.0.0.0", port=5000, debug=True, use_reloader=False
        ), daemon=True)
        api_thread.start()
        while True:
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
        # wallet.join()
        # __logger.info("Wallet stopped")
        exit(0)
    except:
        __logger.exception("Could not start node. Please check config.yml")
        raise

# https://cs.berry.edu/~nhamid/p2p/index.html
