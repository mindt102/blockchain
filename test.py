import yaml

from blockchain import *
from Miner import Miner
from utils import *
from Wallet import Wallet

wallet = Wallet()

config = yaml.load(open('.\\config.yml'), Loader=yaml.FullLoader)
blockchain = Blockchain(config=config["blockchain"])

def is_coin_base(block):
    tx = block.get_transactions()
    if len(tx[0].get_inputs()) > 1:
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

def validate_block(block):
    if CheckBlockHeader(block) == False:
        return False
    if is_coin_base(block) == False:
        return False
    block_merkle_root = compute_merkle_root(block)
    if block_merkle_root != block.get_merkle_root():
        return False
    return True


miner = Miner(config=config["miner"])
#tx = wallet.create_transaction(wallet.get_addr(), 50)
#print(tx)
#print(blockchain.validate_transaction(tx))

# Code
block_test = blockchain.get_genesis_block()
print(block_test)
#print("Check block header: ", CheckBlockHeader(block_test))
#print("Check coin base: ", is_coin_base(block_test))
print("Validate block: ",validate_block(block_test))




