import yaml

from blockchain import *
from Miner import Miner
from utils import *
from Wallet import Wallet

wallet = Wallet()

config = yaml.load(open('.\\config.yml'), Loader=yaml.FullLoader)
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


def check_output_sum(inputs: list[TxIn], outputs: list[TxOut], utxo_set: dict) -> bool:
    '''Check if the sum of the inputs is larger than or equal to the sum of the outputs'''
    #print(inputs)
    print("-----------------------------------------------------")
    #print(outputs)
    
    TxIn_index = inputs[0].get_output_index()
    TxIn_prevtx = inputs[0].get_prev_hash()
    print("input index:", TxIn_index)
    print(tuple((TxIn_prevtx, TxIn_index)))
    archive_index_prev = tuple((TxIn_prevtx, TxIn_index))
    print("----------------------------------------------------")
    print(utxo_set[archive_index_prev].get_amount())
    input_sum = utxo_set[archive_index_prev].get_amount()
    output_sum = outputs[0].get_amount()
    if (input_sum - output_sum) >= 0:
        print("Create money")
        return True
    else: 
        print("Overflow Incident") 


def validate_transaction(tx: Transaction) -> bool:
    '''Validate a transaction'''
    utxo_set = blockchain.get_UTXO_set()
    inputs = tx.get_inputs()
    outputs = tx.get_outputs()

    if len(inputs) == 0 or len(outputs) == 0:
        return False

    for tx_in in inputs:
        if is_spent(tx_in, utxo_set):
            return False

    if not check_output_sum(inputs, outputs, utxo_set):
        return False

    return True


print(validate_transaction(tx))
