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
tx = wallet.create_transaction(wallet.get_addr(), 50)
print(tx)


def is_spent(txin: TxIn, utxo_set: dict) -> bool:
    '''Check if a TxIn is spent'''
    print("TxIn: ", txin)
    print("UTXO: ", utxo_set)
    for key, value in utxo_set.items():
        if txin == value:
            print("----------------------------------------------------------------")
            print("not spent")
            return True
    return False


# def check_output_sum(inputs: list[TxIn], outputs: list[TxOut], utxo_set: dict) -> bool:
#     '''Check if the sum of the inputs is larger than or equal to the sum of the outputs'''
#     input_sum = 0
#     for txin in inputs:
#         index = txin.get_output_index()
#         prevtx = txin.get_prev_tx()
#         key = (index, prevtx)
#         if key not in utxo_set:
#             return False
#         input += utxo_set[key].get_amount()
    
#     output_sum = 0
#     for txout in outputs:
#         output_sum += txout.get_amount()

#     return input_sum >= output_sum

def validate_transaction(tx: Transaction) -> bool:
    '''Validate a transaction'''
    utxo_set = blockchain.get_UTXO_set()
    inputs = tx.get_inputs()
    outputs = tx.get_outputs()
    print("UTXO set: ", utxo_set)

    if len(inputs) == 0 or len(outputs) == 0:
        return False

    # for tx_in in inputs:
        # if tx_in.is_coinbase():
        #     return False
    
    # Calculate total input amount
    input_sum = 0
    for txin in inputs:
        index = txin.get_output_index()
        prevtx = txin.get_prev_tx()
        key = (prevtx, index)

        # Not an unspent transaction outputs
        if key not in utxo_set:
            return False
        input_sum += utxo_set[key].get_amount()
    
    # Calculate total output amount
    output_sum = 0
    for txout in outputs:
        output_sum += txout.get_amount()

    if input_sum < output_sum:
        return False

    return True

print(validate_transaction(tx))
# print(blockchain.validate_transaction(tx))
