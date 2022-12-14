import yaml

from blockchain import *
from Miner import Miner
from utils import *
from Wallet import Wallet

wallet = Wallet()

config = yaml.load(open('.\\config.yml'), Loader=yaml.FullLoader)
blockchain = Blockchain(config=config["blockchain"])


def is_coin_base(tx: Transaction):
    # TODO: Check with algorithm
    inputs = tx.get_inputs()
    # tx = block.get_transactions()
    if len(inputs) != 1:
        return False
    
    first_input = inputs[0]
    prev_tx = first_input.get_prev_tx()
    output_index = first_input.get_output_index()

    if prev_tx != b'\x00' * 32 or output_index != 0xffffffff:
        return False

    return True


def CheckBlockHeader(block):
    block_header_hash = block.get_header().check_hash()
    if block_header_hash == False:
        return False
    return True


def compute_merkle_root(block):
    # TODO: implement
    return block.get_merkle_root()


def validate_block(block: Block):
    # if CheckBlockHeader(block) == False:
    #     return False
    # Use this instead
    if not block.get_header().check_hash():
        return False

    txs = block.get_transactions()
    if not is_coin_base(txs[0]):
        return False

    # block_merkle_root = compute_merkle_root(block)
    block_merkle_root = block.compute_merkle_root()
    if block_merkle_root != block.get_header().get_merkle_root():
        return False

    # TODO: Check other transactions are not coinbase and valid
    for i in range(1, len(txs)):
        tx = txs[i]
        if not blockchain.validate_transaction(tx) or is_coin_base(tx):
            return False
    return True


miner = Miner(config=config["miner"])
#tx = wallet.create_transaction(wallet.get_addr(), 50)
# print(tx)
# print(blockchain.validate_transaction(tx))

# Code
block_test = blockchain.get_genesis_block()
print(block_test)
print("Validate block: ", blockchain.validate_block(block_test))