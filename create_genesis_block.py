'''A script to create a genesis block'''

import argparse
import os

from blockchain import Block, blockchain
from database import genesis_block_path
from Miner import miner


def mine_genesis():
    coinbase_tx = miner.create_coinbase_tx(0)
    candidate_genesis = Block(
        [coinbase_tx], b'\x00'*32, blockchain.get_bits_by_height(0))
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
        print(block.to_json())


# Add -f flag to force overwrite
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force', action='store_true')
args = parser.parse_args()

if args.force:
    mine_genesis()
    exit()

if os.path.exists(genesis_block_path):
    print('Genesis block already exists')
    if input('Do you want to overwrite it? (y/n): ') == 'y':
        mine_genesis()
    else:
        print("Current genesis block:")
        load_genesis()
else:
    mine_genesis()
