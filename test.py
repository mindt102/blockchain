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
transactions = []

for _ in range(1):
    tx = wallet.create_transaction(wallet.get_addr(), random.randint(1, 50))
    transactions.append(tx)

print(transactions)


def compute_merkle_root(transactions: list[Transaction]) -> bytes:
    '''Compute the merkle root of a list of transactions
    Args:
        transactions (list[Transaction]): list of transactions
    Returns:
        bytes: merkle root
    '''
    if len(transactions) == 1:
        merkle_root = hash256(transactions[0].serialize())
    else:
        # TODO: Edit this to compute the merkle root
        pass
    return merkle_root


print(compute_merkle_root(transactions).hex())
