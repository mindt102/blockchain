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

def merkle_parent(arg0, arg1):
    hash0 = bytes.fromhex(arg0)
    hash1 = bytes.fromhex(arg1)
    parent = hash256(hash0+hash1)
    print("Parent hex: ", parent.hex())
    return parent

def compute_merkle_root(transactions: list[Transaction]) -> bytes:
    #Compute the merkle root of a list of transactions
    #Args:
    #    transactions (list[Transaction]): list of transactions
    #Returns:
    #    bytes: merkle root
    if len(transactions) != 1:
        merkle_root = hash256(transactions[0].serialize())
    else:
        # TODO: Edit this to compute the merkle root
        hex_hashes = []
        for _ in range(len(transactions)):
            hash_transac = transactions[_].get_hash()
            hex_hashes.append(hash_transac.hex())
        if len(transactions) % 2 == 1:
                last_hash_transac = transactions[-1].get_hash()
                hex_hashes.append(last_hash_transac.hex())
        Merkle_tree = []
        #while len(hex_hashes) >= 2:
        for i in range(0, len(hex_hashes), 2):
            Merkle_tree.append(merkle_parent(hex_hashes[i], hex_hashes[i+1]))
        merkle_root = Merkle_tree[0]
        pass
    return merkle_root


print(compute_merkle_root(transactions).hex())
