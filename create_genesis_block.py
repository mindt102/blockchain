'''A script to create a genesis block'''

import os

import yaml

import utils
from blockchain import *
from Miner import Miner
from Wallet import Wallet

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

Blockchain = Blockchain(config=config["blockchain"])
genesis_block_path = Blockchain.get_genesis_block_path()

Wallet = Wallet()
Miner = Miner(config=config["miner"])


def mine_genesis():
    coinbase_tx = Miner.create_coinbase_tx()
    candidate_genesis = Block([coinbase_tx], b'\x00'*32, Blockchain.get_bits())
    while True:
        candidate_header = candidate_genesis.get_header()
        if candidate_header.check_hash():
            break
        candidate_header.update_nonce()

    with open(genesis_block_path, 'wb') as f:
        f.write(candidate_genesis.serialize())
    load_genesis()


def load_genesis():
    with open(genesis_block_path, 'rb') as f:
        block = Block.parse(f.read())[0]
        print(block)
        print(int.from_bytes(block.get_header().get_hash()))
        print((utils.bits_to_target(block.get_header().get_bits())))
        print(block.get_header().check_hash())


if os.path.exists(genesis_block_path):
    print('Genesis block already exists')
    if input('Do you want to overwrite it? (y/n): ') == 'y':
        mine_genesis()
    else:
        print("Current genesis block:")
        load_genesis()
else:
    mine_genesis()
