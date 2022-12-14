import yaml

from blockchain import *
from Miner import Miner
from utils import *
from Wallet import Wallet

import random
wallet = Wallet()

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
blockchain = Blockchain(config=config["blockchain"])

miner = Miner(config=config["miner"])
# tx = wallet.create_transaction(wallet.get_addr(), 50)
# print(tx)
# print(blockchain.validate_transaction(tx))