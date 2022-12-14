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
    return False


def check_output_sum(inputs: list[TxIn], outputs: TxOut) -> bool:
    '''Check if the sum of the inputs is larger than or equal to the sum of the outputs'''
    # print(outputs)
    return True


def validate_transaction(tx: Transaction) -> bool:
    '''Validate a transaction'''
    utxo_set = blockchain.get_UTXO_set()
    inputs = tx.get_inputs()
    outputs = tx.get_outputs()

    for tx_in in inputs:
        if is_spent(tx_in, utxo_set):
            return False

    if not check_output_sum(inputs, outputs):
        return False

    return True


print(validate_transaction(tx))
